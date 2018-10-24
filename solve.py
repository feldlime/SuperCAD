"""Module that provides the means to save and solve systems of equations."""

import sympy
import networkx as nx


class EquationsSystem:
    def __init__(self):
        self._symbols = []
        self._graph = nx.MultiGraph()
        self._equations = dict()

    def add_equation(self, equation: sympy.Eq, name: str):
        pass

    def remove_equation(self, equation_name: str):
        pass

    def solve(self):
        pass

    def solve_new(self, equation: sympy.Eq, name: str, add: bool = True):
        pass


class Solver:
    def __init__(self):
        pass

    def solve(self, system):
        pass

