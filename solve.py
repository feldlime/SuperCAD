"""Module that provides the means to save and solve systems of equations."""

import numpy as np
import sympy
import networkx as nx
import scipy.optimize as sp_optimize

from contracts import contract
from itertools import combinations
from collections import OrderedDict

DELIMITER = '___'
SPECIAL_NAME = 'special_name'


def get_full_name(base_name, object_name):
    return f'{base_name}{DELIMITER}{object_name}'


def get_base_name_from_full(full_symbol_name):
    return full_symbol_name.split(DELIMITER, maxsplit=2)[0]


def get_object_name_from_full(full_name):
    return full_name.split(DELIMITER, maxsplit=2)[1]


def get_equation_symbols_names(equation, symbols_names):
    return set([w for w in str(equation).split() if w in symbols_names])


class Substitutor:
    """Class for simplification systems of equations by using substitution of
    simple equations (like x = y or x = 5) to other equations.
    """

    def __init__(self):
        self._subs = dict()
        self._symbols_names = None

    @contract(system='list($sympy.Eq)', symbols_names='list(str)')
    def fit(self, system: list, symbols_names: list):
        """Fit substitutor: save symbols and substitutions.

        Parameters
        ----------
        system: list[sympy.Eq]
            List of equations.
        symbols_names: list[str]
            List of names of all symbols that can be used in equations.

        Returns
        -------
        self
        """
        self._symbols_names = symbols_names

        for eq in system:
            if self._is_simple_equation(eq):
                key = str(eq.lhs)
                value = str(eq.rhs)
                if value.isnumeric():
                    value = float(value)
                self._subs.update({key: value})

        return self

    @contract(system='list($sympy.Eq)', returns='list($sympy.Eq)')
    def sub(self, system: list):
        """Substitute simple equations to others.

        Parameters
        ----------
        system: list[sympy.Eq]
            List of equations.

        Returns
        -------
        new_system: list[sympy.Eq]
            System with substitutions.
        """
        new_system = []
        for eq in system:
            if not self._is_simple_equation(eq):
                new_eq = eq
                for k, v in self._subs.items():
                    new_eq = new_eq.subs(k, v)
                new_system.append(new_eq)
        return new_system

    @contract(solution='dict', returns='dict')
    def restore(self, solution: dict) -> dict:
        """Restore system solution - add to solution variables that have been
        substituted.

        Parameters
        ----------
        solution: dict (str -> float)
            Solution (symbol_name -> value).

        Returns
        -------
        full_solution: dict (str -> float)
            Given solution with added items - variables that were substituted.
        """
        full_solution = solution.copy()

        for k, v in self._subs.items():
            if isinstance(v, str):
                self._subs[k] = solution[k]

        full_solution.update(self._subs)
        return full_solution

    def _is_simple_equation(self, eq):
        """Check if equation is simple (looks like x = y or x = 5)."""
        l_str, r_str = str(eq.lhs), str(eq.rhs)
        if l_str in self._symbols_names \
                and (r_str in self._symbols_names or r_str.isnumeric()):
            return True
        return False


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
    def add_restriction_equations(self, restriction_name: str,
                                  equations: list):
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

    def solve(self, figures: dict):
        result = {}
        for subgraph in nx.connected_component_subgraphs(self._graph):
            equations_names = set([edge[2]['equation_name']
                                   for edge in subgraph.edges(data=True)])
            equations = [self._equations[name] for name in equations_names]
            res = self._solve_system(equations)

    def solve_new(self, equation: sympy.Eq, figures: dict):
        """Solve subsystem with new equation.

        Parameters
        ----------
        equation: sympy.Eq
            New equation.

        Returns
        -------

        """

        graph = self._add_equation_to_graph(self._graph, equation,
                                            equation_name=SPECIAL_NAME)

        equations_names = set()
        for subgraph in nx.connected_component_subgraphs(graph):
            if SPECIAL_NAME not in equations_names:
                continue
            equations_names = set([edge[2]['equation_name']
                                   for edge in subgraph.edges(data=True)])

        equations = [self._equations[name] for name in equations_names]
        res = self._solve_system(equations)

    @classmethod
    @contract(system='list($sympy.Eq)')
    def _solve_system(cls, system: list, symbols_dict: dict):
        symbols_names = list(symbols_dict.keys())

        # Simplify by substitutions
        substitutor = Substitutor()
        simplified_system = substitutor\
            .fit(system, symbols_names)\
            .sub(system)

        # Define symbols that are used
        used_symbols_names = set()
        for eq in simplified_system:
            used_symbols_names\
                .add(get_equation_symbols_names(eq, symbols_names))
        used_symbols_names = list(used_symbols_names)
        used_symbols = [symbols_dict[name] for name in used_symbols_names]

        # Prepare
        canonical_system = cls._system_to_canonical(simplified_system)
        system_function = \
            cls._system_to_function(canonical_system, used_symbols)

        # Solve
        init = np.random.random(len(used_symbols))  # TODO: use current values
        solution = cls._solve_numeric(system_function, init)

        # Add values for symbols that were substituted
        solution_dict = dict(zip(used_symbols_names, solution))
        full_solution_dict = substitutor.restore(solution_dict)

        return full_solution_dict

    @staticmethod
    @contract(system='list[N>0]($sympy.Eq)', symbols='list[N]($sympy.Symbol)')
    def _system_to_function(system: list, symbols: list):
        functions = [sympy.lambdify(symbols, f) for f in system]

        def fun(x):
            if len(x) != len(symbols):
                raise ValueError
            res = np.array([f(*x) for f in functions])
            return res

        return fun

    @staticmethod
    @contract(system='list[N>0]($sympy.Eq)')
    def _system_to_canonical(system: list):
        return [eq.lhs - eq.rhs for eq in system]

    @staticmethod
    def _solve_numeric(fun: function, init: np.ndarray) -> np.ndarray:
        result = sp_optimize.fsolve(fun, init)
        return result[0]

    def _update_graph(self):
        graph = nx.Graph()
        graph.add_nodes_from(self._symbols)
        for eq_name, eq in self._equations.items():
            self._add_equation_to_graph(graph, eq, equation_name=eq_name)
        self._graph = graph

    @staticmethod
    @contract(equation='$sympy.Eq', equation_name='str | None')
    def _add_equation_to_graph(graph, equation, equation_name=None):
        g = graph.copy()
        eq_symbols = get_equation_symbols_names(equation, g.nodes)

        if len(eq_symbols) < 2:
            # raise RuntimeError('To few symbols in equation.')
            pass
        else:
            for u, v in combinations(eq_symbols, 2):
                graph.add_edge(u, v, equation_name=equation_name)

        return g
