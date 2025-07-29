# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import asyncio
import quattro
import collections
import json
import pathlib
import webbrowser
from graphlib import TopologicalSorter
import logging

from sammo.utils import HtmlRenderer, GRAPH_TEMPLATE

logger = logging.getLogger(__name__)


class ComputeNode:
    __slots__ = ["job", "compute_context", "priority", "needs_scheduling"]

    def __init__(self, job, local_cache, priority):
        self.job = job
        self.compute_context = local_cache
        self.priority = priority


class Scheduler:
    def __init__(self, runner, jobs, base_priority=0):
        # Construct graph
        self._graph = dict()
        self._runner = runner

        jobs = [jobs] if not isinstance(jobs, collections.abc.Iterable) else jobs
        queue = [ComputeNode(x, x._context, i) for i, x in enumerate(jobs)]

        self._graph = dict()
        while queue:
            x = queue.pop(0)
            children = [ComputeNode(c, x.compute_context, x.priority + i) for i, c in enumerate(x.job.dependencies)]
            queue = children + queue
            self._graph[x] = set(children)

        self.tasks = TopologicalSorter(self._graph)
        self.tasks.prepare()
        self.finalized_tasks_queue = asyncio.Queue()

    @staticmethod
    def _generate_id(node, iddict):
        if node not in iddict:
            iddict[node] = f"{node.job.__class__.__name__}_{node.priority}_{len(iddict)}"

    def plot(self, open_in_browser=False):
        elements = self._to_html()

        # write out as utf-8 file
        file = pathlib.Path("logs/callgraph.html")
        with open(file, "w", encoding="utf-8") as f:
            f.write()
        if open_in_browser:
            webbrowser.open(file.absolute().as_uri(), new=2, autoraise=False)

    def _to_html(self):
        # Generate ids
        node_ids = dict()
        for node, children in self._graph:
            self.generate_id(node, node_ids)
            for child in children:
                self.generate_id(child, node_ids)
        # Convert into Cytoscape.js format
        nodes = [{"data": {"id": v}} for v in node_ids.values()]
        edges = list()
        for e1, v in self._graph.items():
            for e2 in v:
                e1_id = node_ids[e1]
                e2_id = node_ids[e2]
                edges.append({"data": {"id": f"{e1_id}_{e2_id}", "source": e1_id, "target": e2_id}})
        elements = {"nodes": nodes, "edges": edges}
        return GRAPH_TEMPLATE.replace("ELEMENTS", json.dumps(elements, ensure_ascii=False))

    def display(self, backend="auto"):
        return HtmlRenderer(self._to_html()).render(backend)

    async def run_node(self, node):
        await node.job(self._runner, node.compute_context, None)
        await self.finalized_tasks_queue.put(node)

    async def arun(self):
        async with quattro.TaskGroup() as tg:
            while self.tasks.is_active():
                for compute_node in self.tasks.get_ready():
                    if compute_node.job.NEEDS_SCHEDULING:
                        tg.create_task(self.run_node(compute_node))
                    else:
                        await self.finalized_tasks_queue.put(compute_node)

                compute_node = await self.finalized_tasks_queue.get()
                self.tasks.done(compute_node)

    def run(self):
        asyncio.run(self.arun())
