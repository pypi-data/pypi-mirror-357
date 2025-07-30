from dataclasses import dataclass
from typing import override

import networkx as nx
from quark.core import Core, Data, Result
from quark.interface_types import Graph, Other


@dataclass
class ClassicalMisSolver(Core):
    """
    Module for solving the MIS problem using a classical solver
    """

    @override
    def preprocess(self, data: Graph) -> Result:
        self._solution = nx.approximation.maximum_independent_set(data.as_nx_graph())
        return Data(None)

    @override
    def postprocess(self, data: None) -> Result:
        return Data(Other(self._solution))
