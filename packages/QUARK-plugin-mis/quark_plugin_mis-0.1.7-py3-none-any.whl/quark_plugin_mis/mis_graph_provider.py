import logging
import math
from dataclasses import dataclass
from typing import override

import networkx as nx
import pulser
from numpy import random
from quark.core import Core, Data, Result
from quark.interface_types import Graph, Other

R_rydberg = 9.75


@dataclass
class MisGraphProvider(Core):
    graph_type: str = "hexagonal"
    size: int = 3
    spacing: int = 1
    filling_fraction: float = 0.5
    seed: int = 0
    k: int = 2
    p: float = 0.75

    @override
    def preprocess(self, data: None) -> Result:
        match self.graph_type:
            case "erdosRenyi":
                graph = nx.erdos_renyi_graph(
                    self.size, self.filling_fraction, seed=self.seed
                )
                logging.info(
                    "Created MIS problem with the nx.erdos_renyi graph method, with the following attributes:"
                )
                logging.info(f" - Graph size: {self.size}")
                logging.info(f" - p: {self.filling_fraction}")
                logging.info(f" - seed: {self.seed}")

            case "hexagonal":
                graph = self._generate_hexagonal_graph(
                    n_nodes=self.size,
                    spacing=self.spacing * R_rydberg,
                    filling_fraction=self.filling_fraction,
                )
                logging.info(
                    "Created MIS problem with the generate hexagonal graph method, with the following attributes:"
                )
                logging.info(f" - Graph size: {self.size}")
                logging.info(f" - Spacing: {self.spacing * R_rydberg}")
                logging.info(f" - Filling fraction: {self.filling_fraction}")

            case "newmanWattsStrogatz":
                graph = nx.newman_watts_strogatz_graph(
                    self.size, self.k, self.p, self.seed
                )
                logging.info(
                    "Created MIS problem with the newmanWattsStrogatz graph method, with the following attributes:"
                )
                logging.info(f" - Graph size: {self.size}")
                logging.info(f" - K nearest neighbors: {self.k}")
                logging.info(f" - Edge probability: {self.p}")
                logging.info(f" - Seed: {self.seed}")
            case _:
                raise NotImplementedError(
                    f"Graph type {self.graph_type} is not implemented."
                )

        self._graph = graph
        return Data(Graph.from_nx_graph(graph.copy()))

    @override
    def postprocess(self, data: Other) -> Result:
        solution = data.data

        is_valid = True

        nodes = list(self._graph.nodes())
        edges = list(self._graph.edges())

        # Check if the solution is independent
        is_independent = all(
            (u, v) not in edges for u, v in edges if u in solution and v in solution
        )
        if is_independent:
            logging.info("The solution is independent.")
        else:
            logging.warning("The solution is not independent.")
            is_valid = False

        # Check if the solution is a set
        solution_set = set(solution)
        is_set = len(solution_set) == len(solution)
        if is_set:
            logging.info("The solution is a set.")
        else:
            logging.warning("The solution is not a set.")
            is_valid = False

        # Check if the solution is a subset of the original nodes
        is_subset = all(node in nodes for node in solution)
        if is_subset:
            logging.info("The solution is a subset of the problem.")
        else:
            logging.warning("The solution is not a subset of the problem.")
            is_valid = False

        if not is_valid:
            # TODO
            pass

        set_size = len(solution)

        logging.info(f"Size of solution: {set_size}")

        return Data(Other(data=set_size))

    @staticmethod
    def _vertex_distance(v0: tuple[float, ...], v1: tuple[float, ...]) -> float:
        """
        Calculates distance between two n-dimensional vertices.
        For 2 dimensions: distance = sqrt((x0 - x1)**2 + (y0 - y1)**2)

        :param v0: Coordinates of the first vertex
        :param v1: Coordinates of the second vertex
        return: Distance between the vertices
        """
        squared_difference = sum(
            (coordinate0 - coordinate1) ** 2 for coordinate0, coordinate1 in zip(v0, v1)
        )

        return math.sqrt(squared_difference)

    @staticmethod
    def _generate_edges(node_positions: dict, radius: float = R_rydberg) -> list[tuple]:
        """
        Generate edges between vertices within a given distance 'radius', which defaults to R_rydberg.

        :param node_positions: A dictionary with the node ids as keys, and the node coordinates as values
        :param radius: When the distance between two nodes is smaller than this radius, an edge is generated between them
        :return: A list of 2-tuples. Each 2-tuple contains two different node ids and represents an edge between those nodes
        """
        edges = []
        vertex_keys = list(node_positions.keys())
        for i, vertex_key in enumerate(vertex_keys):
            for neighbor_key in vertex_keys[i + 1 :]:
                distance = MisGraphProvider._vertex_distance(
                    node_positions[vertex_key], node_positions[neighbor_key]
                )
                if distance <= radius:
                    edges.append((vertex_key, neighbor_key))
        return edges

    @staticmethod
    def _generate_hexagonal_graph(
        n_nodes: int, spacing: float, filling_fraction: float = 1.0
    ) -> nx.Graph:
        """
        Generate a hexagonal graph layout based on the number of nodes and spacing.

        :param n_nodes: The number of nodes in the graph
        :param spacing: The spacing between nodes (atoms)
        :param filling_fraction: The fraction of available places in the lattice to be filled with nodes. (default: 1.0)
        :return: Networkx Graph representing the hexagonal graph layout
        """
        if not 0.0 < filling_fraction <= 1.0:
            raise ValueError(
                "The filling fraction must be in the domain of (0.0, 1.0]."
            )

        # Create a layout large enough to contain the desired number of atoms at the filling fraction
        n_traps = int(n_nodes / filling_fraction)
        hexagonal_layout = pulser.register.special_layouts.TriangularLatticeLayout(  # type: ignore
            n_traps=n_traps, spacing=spacing
        )

        # Fill the layout with traps
        reg = hexagonal_layout.hexagonal_register(n_traps)
        ids = reg._ids
        coords = [coord.tolist() for coord in reg._coords]
        traps = dict(zip(ids, coords))

        # Remove random atoms to get the desired number of atoms
        while len(traps) > n_nodes:
            atom_to_remove = random.choice(list(traps))
            traps.pop(atom_to_remove)

        # Rename the atoms
        node_positions = {i: traps[trap] for i, trap in enumerate(traps.keys())}

        # Create the graph
        hexagonal_graph = nx.Graph()

        # Add nodes to the graph
        for node_id, coord in node_positions.items():
            hexagonal_graph.add_node(node_id, pos=coord)

        # Generate the edges and add them to the graph
        edges = MisGraphProvider._generate_edges(node_positions=node_positions)
        hexagonal_graph.add_edges_from(edges)

        return hexagonal_graph
