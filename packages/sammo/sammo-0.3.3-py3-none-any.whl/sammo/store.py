# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Implements two different types of dictionaries that can store either data in memory or on disk. Allows keys to be
arbitrary JSON-serializable objects that get rendered to byte strings for indexing.
Mainly used to cache LLM API calls, but can be used for other purposes as well.
"""
from __future__ import annotations
from collections.abc import MutableMapping
from contextlib import ExitStack
from io import BytesIO
import logging
import os
import threading
import warnings
from pathlib import Path

import diskcache
from beartype.typing import Callable, Union
import filelock
import orjson
from pyglove import JSONConvertible

from sammo.utils import CodeTimer
from sammo.utils import serialize_json as serialize_json_obj

__all__ = ["PersistentDict", "InMemoryDict"]

logger = logging.getLogger(__name__)


def serialize_json(obj):
    if isinstance(obj, bytes):
        return obj
    else:
        return serialize_json_obj(obj)


class PersistentDict(MutableMapping, JSONConvertible):
    """
    Implements a dictionary that is persisted to disk. Entries are appended to the end of the file, with later entries
    overwriting earlier ones. The file is read into memory on initialization to allow for fast lookups.
    Write and delete operations are thread-safe.

    :param filename:
      path for the stored data. Loads the dictionary from the given file, or creates a new one if it doesn't exist.
    """

    def __init__(self, filename: os.PathLike | str):
        self._filename = Path(filename)
        if self._filename.exists():
            self._dict = self._load()
        else:
            self._filename.parent.mkdir(parents=True, exist_ok=True)
            self._dict = dict()
        self._fp = None
        self._lock = threading.Lock()
        self._os_lock = filelock.FileLock(self._filename.with_suffix(".lock"), timeout=1)

    def _load(self):
        timer = CodeTimer()
        keys, vals = list(), list()
        for line in open(self._filename, "rb"):
            if line[0] == b"#" or line == b"\n" or b"\t" not in line:
                continue
            splits = line.split(b"\t", 2)
            if len(splits) != 2:
                continue
            key, val = splits
            try:
                val = orjson.loads(val)
                keys.append(key)
                vals.append(val)
            except orjson.JSONDecodeError:
                logger.warning(f"Failed to load line {line}")
        logger.info(f"Loaded {len(keys)} entries from {self._filename} in {timer.interval:.2f} s")
        return dict(zip(keys, vals))

    def _append_to_file(self, key, value):
        if self._fp is None:
            self._filename.parent.mkdir(parents=True, exist_ok=True)
            if not self._filename.exists():
                self._fp = open(self._filename, "wb")
            else:
                self._fp = open(self._filename, "r+b")
            self._fp.seek(0, os.SEEK_END)

        # Mark the new line as a comment until fully written out
        offset = self._fp.tell()

        if offset > 0:
            self._fp.write(b"\n")

        offset = self._fp.tell()
        self._fp.write(b"#")
        self._fp.write(key[1:])
        self._fp.write(b"\t")
        self._fp.write(orjson.dumps(value))
        self._fp.flush()

        # Remove the comment marker
        self._fp.seek(offset)
        self._fp.write(key[0:1])
        self._fp.seek(0, os.SEEK_END)
        self._fp.flush()
        if not type(self._fp) == BytesIO:
            os.fsync(self._fp.fileno())

    def vacuum(self) -> None:
        """Removes all deleted entries from the file."""
        tmp_fname = self._filename.with_suffix(".tmp")
        with self._lock:
            with open(tmp_fname, "wb") as f:
                for key, value in self._dict.items():
                    if value is not None:
                        f.write(key)
                        f.write(b"\t")
                        f.write(orjson.dumps(value, option=orjson.OPT_APPEND_NEWLINE))
            if self._fp:
                self._fp.close()
                self._fp = None
            os.replace(tmp_fname, self._filename)

    def __contains__(self, key):
        bkey = self._find(key)
        return bkey in self._dict and self._dict[bkey] is not None

    def __getitem__(self, key):
        return self._dict[self._find(key)]

    def __getstate__(self):
        return self._dict

    def __setstate__(self, state):
        self._dict = state

    def _find(self, key):
        return serialize_json(key)

    def __setitem__(self, key, value):
        bkey = serialize_json(key)
        with self._lock:
            with self._os_lock:
                self._append_to_file(bkey, value)
            self._dict[bkey] = value

    def __delitem__(self, key):
        # Convention: deleted items set to None
        bkey = self._find(key)
        if bkey in self._dict:
            with self._lock:
                with self._os_lock:
                    self._append_to_file(bkey, None)
                del self._dict[bkey]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def to_json(self, **kwargs):
        return {"_type": "PersistentDict", "filename": str(self._filename)}

    @classmethod
    def from_json(cls, json_value, **kwargs):
        return cls(json_value["filename"])


class InMemoryDict(PersistentDict):
    """
    Implements a dictionary that lives only in memory. Entries are not persisted to disk unless `persist` is called.

    """

    def __init__(self):
        self._dict = dict()
        self._lock = threading.Lock()
        self._os_lock = ExitStack()

    def _append_to_file(self, key, value):
        pass

    def persist(self, filename: os.PathLike | str):
        """Persists the dictionary to disk.

        :param filename: path for the stored data.
        """
        with open(filename, "wb") as f:
            for key, value in self._dict.items():
                if value is not None:
                    f.write(key)
                    f.write(b"\t")
                    f.write(orjson.dumps(value, option=orjson.OPT_APPEND_NEWLINE))


class SqlLiteDict(PersistentDict):
    """
    Implements a dictionary that is persisted to disk a SQLite DB. It is a bit slower for shorter entries than using
    PersistentDict which is all buffered in memory, but preferable when storing larger objects, such as vectors.

    :param directory: path for the stored data. If none, uses a temporary directory.
    """

    def __init__(self, directory: Union[os.PathLike, str, None] = None):
        if directory and Path(directory).exists() and not Path(directory).is_dir():
            raise ValueError(f"{directory} is not a directory.")
        self._filename = directory
        self._dict = diskcache.Cache(directory, eviction_policy="none")

    def vacuum(self) -> None:
        pass

    def _find(self, key):
        return serialize_json(key)

    def __contains__(self, key):
        return self._find(key) in self._dict

    def __setitem__(self, key, value):
        self._dict[self._find(key)] = value

    def __delitem__(self, key):
        del self._dict[self._find(key)]

    def to_json(self, **kwargs):
        return {"_type": "SqlLiteDict", "filename": str(self._filename)}
