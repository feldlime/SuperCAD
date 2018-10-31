"""Module that provides the means to save and solve systems of equations."""

import numpy as np
import sympy
import networkx as nx
from scipy.optimize import (
    broyden1,
    broyden2,
    newton_krylov,
    anderson
)

from contracts import contract

DELIMITER = '___'


def get_full_symbol_name(object_name, symbol_name):
    return f'{object_name}{DELIMITER}{symbol_name}'


def get_pure_symbol_name(full_symbol_name):
    return full_symbol_name.split(DELIMITER, maxsplit=2)[1]


def get_object_name(full_symbol_name):
    return full_symbol_name.split(DELIMITER, maxsplit=2)[0]


class EquationsSystem:
    def __init__(self):
        self._symbols = dict()
        self._graph = nx.MultiGraph()
        self._equations = dict()

    def add_symbols(self, object_name: str, symbols_names: str):
        symbols_names = [get_full_symbol_name(object_name, sym)
                         for sym in symbols_names]
        new_symbols = {name: sympy.symbols(name) for name in symbols_names}
        self._symbols.update(new_symbols)
        self._update_graph()

    def get_symbols(self, object_name: str, symbol_name: str = None):
        if symbol_name is not None:
            symbol_name = get_full_symbol_name(object_name, symbol_name)
            # TODO: check name
            return self._symbols[symbol_name]
        else:
            result = {get_pure_symbol_name(name): sym
                      for name, sym in self._symbols
                      if get_object_name(name) == object_name}
            return result

    def add_equation(self, equation: sympy.Eq, name: str):
        # TODO
        self._update_graph()

    def remove_equation(self, equation_name: str):
        # TODO
        self._update_graph()

    def solve(self):
        pass

    def solve_new(self, equation: sympy.Eq, name: str = None,
                  add: bool = True):
        """Solve subsystem with new equation

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

    def _update_graph(self):
        pass

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
    pass

