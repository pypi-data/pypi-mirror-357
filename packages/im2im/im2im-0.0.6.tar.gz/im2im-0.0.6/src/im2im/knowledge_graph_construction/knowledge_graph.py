from typing import Union, List

import networkx as nx
from heapq import heappush, heappop

from .io import save_graph, load_graph
from .metedata import Metadata, encode_metadata, decode_metadata


class KnowledgeGraph:
    _graph = None

    def __init__(self):
        self._graph = nx.DiGraph()

    def clear(self):
        self._graph.clear()

    @property
    def nodes(self):
        encoded_nodes = self._graph.nodes
        return [decode_metadata(node) for node in encoded_nodes]

    @property
    def edges(self):
        encoded_edges = self._graph.edges
        return [
            (decode_metadata(edge[0]), decode_metadata(edge[1]))
            for edge in encoded_edges
        ]

    def add_node(self, node):
        self._graph.add_node(encode_metadata(node))

    def add_edge(
        self,
        source: Metadata,
        target: Metadata,
        conversion,
        factory=None,
    ):
        self._graph.add_edge(
            encode_metadata(source),
            encode_metadata(target),
            conversion=conversion,
            factory=factory,
        )

    def get_edge_data(self, source: Metadata, target: Metadata):
        return self._graph.get_edge_data(
            encode_metadata(source), encode_metadata(target)
        )

    def set_edge_attribute(self, source: Metadata, target: Metadata, attribute, value):
        self._graph[encode_metadata(source)][encode_metadata(target)][attribute] = value

    def save_to_file(self, path):
        save_graph(self._graph, path)

    def load_from_file(self, path):
        self._graph = load_graph(path)

    def get_shortest_path(
        self, source_metadata, target_metadata, huristic_function, accept_lossy_path=True
    ) -> Union[List[str], None]:
        target_metadata_str = encode_metadata(target_metadata)
        # Priority queue: stores (cost, node, path)
        pq = []
        heappush(pq, ((0, 0), encode_metadata(source_metadata), []))

        visited = set()

        while pq:
            current_cost, current_node, path = heappop(pq)

            if current_node == target_metadata_str:
                return [decode_metadata(node) for node in path] + [target_metadata]

            if current_node in visited:
                continue

            visited.add(current_node)

            for neighbor in self._graph.neighbors(current_node):
                edge_data = self._graph.get_edge_data(current_node, neighbor)
                if 'conversion' not in edge_data:
                    continue

                goal_cost = tuple(x + y for x, y in zip(current_cost, edge_data["conversion"][2]))
                if huristic_function is None:
                    total_cost = goal_cost
                else:
                    huristic = huristic_function(neighbor, target_metadata_str)
                    total_cost = tuple(x + y for x, y in zip(goal_cost, huristic))
                if not accept_lossy_path and total_cost[0] > 0:
                    continue

                # storing the cost (tuples) are compared lexicographically.
                heappush(pq, (total_cost, neighbor, path + [current_node]))

        return None

    def __str__(self):
        return f"Knowledge Graph with {len(self._graph)} nodes and {len(self._graph.edges)} edges."
