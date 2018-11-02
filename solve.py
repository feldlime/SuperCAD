"""Module that provides the means to save and solve systems of equations."""

import numpy as np
import sympy
import networkx as nx
from scipy.optimize import root

from contracts import contract
from itertools import combinations

DELIMITER = '___'


def get_full_name(base_name, object_name):
    return f'{base_name}{DELIMITER}{object_name}'


def get_base_name_from_full(full_symbol_name):
    return full_symbol_name.split(DELIMITER, maxsplit=2)[0]


def get_object_name_from_full(full_name):
    return full_name.split(DELIMITER, maxsplit=2)[1]


class EquationsSystem:
    def __init__(self):
        self._symbols = dict()
        self._equations = dict()

        self._graph = nx.Graph()

    @contract(figure_name='str', symbols_names='list(str)')
    def add_figure_symbols(self, figure_name: str, symbols_names: list):
        symbols_names = [get_full_name(figure_name, sym)
                         for sym in symbols_names]
        new_symbols = {name: sympy.symbols(name) for name in symbols_names}
        self._symbols.update(new_symbols)
        self._update_graph()

    @contract(figure_name='str', symbol_name='str | None')
    def get_symbols(self, figure_name: str, symbol_name: str = None):
        if symbol_name is not None:
            symbol_name = get_full_name(figure_name, symbol_name)
            if symbol_name not in self._symbols:
                raise ValueError('No such symbol.')
            return self._symbols[symbol_name]
        else:
            result = {get_object_name_from_full(name): sym
                      for name, sym in self._symbols
                      if get_base_name_from_full(name) == figure_name}
            return result

    @contract(figure_name='str')
    def remove_figure_symbols(self, figure_name: str):
        symbols_to_delete = [
            name for name in self._symbols.keys()
            if get_base_name_from_full(name) == figure_name
        ]
        if not symbols_to_delete:
            raise RuntimeError('No symbols were found.')
        for symbol_name in symbols_to_delete:
            self._symbols.pop(symbol_name)
        self._update_graph()

    @contract(restriction_name='str', symbols_names='list($sympy.Eq)')
    def add_restriction_equations(self, restriction_name: str, equations: list):
        equations_names = [get_full_name(restriction_name, i)
                           for i in range(len(equations))]
        new_equations = {name: eq
                         for name, eq in zip(equations_names, equations)}
        self._equations.update(new_equations)
        self._update_graph()

    @contract(restriction_name='str', symbols_names='list($sympy.Eq)')
    def remove_restriction_equations(self, restriction_name: str):
        equations_to_delete = [
            name for name in self._equations.keys()
            if get_base_name_from_full(name) == restriction_name
        ]
        if not equations_to_delete:
            raise RuntimeError('No equations were found.')
        for equation_name in equations_to_delete:
            self._equations.pop(equation_name)
        self._update_graph()

    def solve(self):


    def solve_new(self, equation: sympy.Eq, name: str = None,
                  add: bool = True):
        """Solve subsystem with new equation.

        Parameters
        ----------
        equation: sympy.Eq
            New equation.
        name: str
            Name of equation.
        add: bool
            If True, equation will be added to system.

        Returns
        -------

        """

    def _solve_system(self, system):
        # Do subs



    def _update_graph(self):
        graph = nx.Graph()

        graph.add_nodes_from(self._symbols)

        for eq in self._equations.values():
            eq_symbols = set()

            for word in str(eq).split():
                if word in graph.nodes:
                    eq_symbols.add(word)

            if len(eq_symbols) < 2:
                raise RuntimeError('To few symbols in equation.')
            else:
                for u, v in combinations(eq_symbols, 2):
                    graph.add_edge(u, v)

        self._graph = graph


    @contract(system='list[N>0]($sympy.Eq)')
    def _system_to_function(self, system):
        system = [eq.lhs - eq.rhs for eq in system.values()]

        functions = [sympy.lambdify(self._symbols, f) for f in system]

        def fun(x):
            if len(x) != len(self._symbols):
                raise ValueError
            res = np.array([f(*x) for f in functions])
            return res

        return fun


def solve(system: function):
    result = root(system)
    return result

