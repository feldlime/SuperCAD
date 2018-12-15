"""Module that provides the means to save and solve systems of equations."""

from numpy import array as np_array, ndarray as np_ndarray, random
from sympy import (
    Eq,
    Symbol,
    lambdify,
    true as sympy_true,
    false as sympy_false,
    Integer as sympy_Integer
)

import networkx as nx
import scipy.optimize as sp_optimize

from contracts import contract, new_contract
from itertools import combinations
from collections import defaultdict
import re
import types

from utils import IncorrectParamValue, BIG_NUMBER

from diagnostic_context import measure, measured, measured_total, measure_total, DEFAULT_CONTEXT_TOTAL as context_total


DELIMITER = '___'
SPECIAL_NAME = 'special_name'
GROWTH_NODE_NAME = 'growth_node'

figures_values_contract = new_contract('figures_values',
                                       'dict(str: dict(str: float))')

number_pattern = re.compile(r'-?[ ]?\d+\.?\d*')

empty_dict = types.MappingProxyType({})


@contract(base_name='str', object_name='str', returns='str')
def compose_full_name(base_name: str, object_name: str) -> str:
    return f'{base_name}{DELIMITER}{object_name}'


@contract(full_name='str', returns='list[2](str)')
def split_full_name(full_name: str) -> (str, str):
    return full_name.split(DELIMITER, maxsplit=2)


@contract(flatten_dict='dict(str: float)', returns='figures_values')
def roll_up_values_dict(flatten_dict: dict) -> dict:
    """Make hierarchical dictionary from flatten.

    Parameters
    ----------
    flatten_dict: str -> any
        Dictionary full_name -> value.

    Returns
    ----------
    hierarchical_dict: str -> (str -> any)
        Dictionary base_name -> (object_name -> value).
    """
    result = defaultdict(dict)
    for full_name, value in flatten_dict.items():
        base_name, object_name = split_full_name(full_name)
        result[base_name][object_name] = value
    return dict(result)


@contract(hierarchical_dict='figures_values', returns='dict(str: float)')
def unroll_values_dict(hierarchical_dict: dict) -> dict:
    """Make flatten dictionary from hierarchical.

    Parameters
    ----------
    hierarchical_dict: str -> (str -> any)
        Dictionary base_name -> (object_name -> value).

    Returns
    ----------
    flatten_dict: str -> any
        Dictionary full_name -> value.
    """
    result = dict()
    for base_name, base_values in hierarchical_dict.items():
        for object_name, value in base_values.items():
            full_name = compose_full_name(base_name, object_name)
            result[full_name] = value
    return result


@contract(symbols_names='list(str)')
def get_equation_symbols_names(equation: Eq, symbols_names: list) -> set:
    # res =  set([w for w in symbols_names if w in str(equation)])
    str_atoms = [str(a) for a in equation.atoms()]
    res = set([w for w in symbols_names if w in str_atoms])
    return res


class CannotSolveSystemError(Exception):
    pass


class MoreEquationsThanSymbolsError(CannotSolveSystemError):
    """
    We don't now, can be system solved or not,
    but we cannot try to solve it.
    """
    pass


class SystemOverfittedError(CannotSolveSystemError):
    """
    System contains similar equations
    e.g. [x = 5, x = 5] or [x = 5, x = 10]
    """
    pass


class SystemIncompatibleError(SystemOverfittedError):
    """
    System contains conflicting equations,
    e.g. [x = y, x = 5, y = 10].
    """
    pass


class SubstitutionError(Exception):
    pass


class Substitutor:
    """Class for simplification systems of equations by using substitution of
    simple equations (like x = y or x = 5) to other equations.
    """

    def __init__(self):
        self._subs = dict()  # str -> Union[Symbol, float]
        self._symbols_dict = None  # str -> Symbol

    @property
    def subs(self):
        return dict(self._subs)

    @contract(system='list', symbols_dict='dict(str: *)')
    def fit(self, system: list, symbols_dict: dict):
        """Fit substitutor: save symbols and substitutions.

        Parameters
        ----------
        system: list[sympy.Eq]
            List of equations.
        symbols_dict: list[str]
            Dict (sym_name -> sym) of all symbols that can be used in equations.

        Returns
        -------
        self
        """
        self._symbols_dict = symbols_dict

        # ### Define and save simple equations

        # At first, go through all simple equations,
        # swap if, e.g. 5 = 'x',
        # if value is number, save it to self._subs
        # else save to symbols dict
        sym2sym_dict = dict()
        for eq in system:
            if self._is_simple_equation(eq):
                key = str(eq.lhs)
                value = str(eq.rhs)

                if re.fullmatch(number_pattern, key):
                    if value in self._subs:
                        raise SubstitutionError('Two same keys.')
                    self._subs[value] = float(key)
                elif re.fullmatch(number_pattern, value):
                    if key in self._subs:
                        raise SubstitutionError('Two same keys.')
                    self._subs[key] = float(value)
                else:
                    if key in sym2sym_dict and sym2sym_dict[key] == value:
                        # Case when value in keys() and key in values() will
                        # be treated later
                        raise SubstitutionError('Two same equations.')
                    sym2sym_dict[key] = value

        # Then treat cases with 2 values
        # So much code to treat different cases
        # E.g. x=y, y=z, y=5 -> x: 5, y: 5, z: 5

        # Graph to find connected_components and cycles
        graph = nx.Graph()
        for key, value in sym2sym_dict.items():
            if (key, value) in graph.edges:  # order is not important
                raise SubstitutionError('Two same equations.')
            if key not in graph.nodes:
                graph.add_node(key)
            if value not in graph.nodes:
                graph.add_node(value)
            graph.add_edge(key, value)

        # If there is cycle in graph, system is underfited (a=b, b=c, c=a)
        try:
            nx.find_cycle(graph)
        except nx.NetworkXNoCycle:
            pass
        else:
            raise SubstitutionError('Cycle in equations graph.')

        subgraphs = [graph.subgraph(c).copy()
                     for c in nx.connected_components(graph)]
        for subgraph in subgraphs:
            nodes_in_subs = [node for node in subgraph.nodes
                             if node in self._subs]

            if len(nodes_in_subs) > 1:  # overfitted
                raise SubstitutionError('Substitutor get two same keys.')

            elif len(nodes_in_subs) == 1:  # has value for all nodes
                key_node = nodes_in_subs[0]
                for node in subgraph.nodes:
                    if node != key_node:
                        self._subs[node] = self._subs[key_node]

            else:  # len == 0 (no value for nodes)
                iter_ = iter(subgraph.nodes)
                key_node = next(iter_)
                for node in iter_:
                    if node != key_node:
                        self._subs[node] = self._symbols_dict[key_node]

        return self

    @contract(system='list', returns='list')
    def sub(self, system: list) -> list:
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
                new_eq = eq.subs([(sym_name, value) for sym_name, value in self._subs.items()])
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

        try:
            for k, v in self._subs.items():
                if not isinstance(v, float):
                    self._subs[k] = solution[str(v)]  # v must be in solution
        except KeyError:
            raise RuntimeError(f'Symbol {v} not in solution')

        full_solution.update(self._subs)
        return full_solution

    @measured_total
    def _is_simple_equation(self, eq):
        """Check if equation is simple (looks like x = y or x = 5)."""
        l_str, r_str = str(eq.lhs), str(eq.rhs)

        if l_str in self._symbols_dict:
            ltype = 'sym'
        elif re.fullmatch(number_pattern, l_str):
            ltype = 'num'
        else:
            return False

        if r_str in self._symbols_dict:
            return True
        elif re.fullmatch(number_pattern, r_str) and ltype == 'sym':
            return True
        else:
            return False


class EquationsSystem:
    def __init__(self):
        self._symbols = dict()
        self._equations = dict()
        self._graph = nx.MultiGraph()

    @property
    def _figures_names(self):
        return list(set([split_full_name(name)[0] for name in self._symbols]))

    @property
    def _restrictions_names(self):
        return list(set([split_full_name(nam)[0] for nam in self._equations]))

    @contract(figure_name='str', symbols_names='list(str)')
    def add_figure_symbols(self, figure_name: str, symbols_names: list):
        """
        Add symbols for one figure.
        Cannot add symbols for existing figure.

        Parameters
        ----------
        figure_name: str
            Name of figure.
        symbols_names: list[str]
            Names f symbols for figure.

        Raises
        ------
        IncorrectParamValue: if given figure has already exist.
        """
        if figure_name in self._figures_names:
            raise IncorrectParamValue(
                f'Figure {figure_name} has already exist.')

        symbols_names = [compose_full_name(figure_name, sym)
                         for sym in symbols_names]
        new_symbols = {name: Symbol(name)  # TODO: real=True
                       for name in symbols_names}
        self._symbols.update(new_symbols)
        self._update_graph()

    @contract(figure_name='str', symbol_name='str | None')
    def get_symbols(self, figure_name: str, symbol_name: str = None):
        """
        Return symbols for one figure.

        Parameters
        ----------
        figure_name: str
            Name of figure.
        symbol_name: str or None, optional, default None
            If string, returns symbol with this name.
            If None, returns dictionary with all symbols of given figure.

        Returns
        -------
            symbols or symbol: dict(str -> sympy.Symbol) or sympy.Symbol

        Raises
        ------
            IncorrectParamValue: if there is no such figure or if symbol name
            is given, but such symbol for such figure does not exist.
        """
        if figure_name not in self._figures_names:
            raise IncorrectParamValue(f'Figure {figure_name} does not exist.')

        if symbol_name is not None:
            symbol_name = compose_full_name(figure_name, symbol_name)
            if symbol_name not in self._symbols:
                raise IncorrectParamValue('No such symbol.')
            return self._symbols[symbol_name]
        else:
            result = dict()
            for name, sym in self._symbols.items():
                base_name, object_name = split_full_name(name)
                if base_name == figure_name:
                    result[object_name] = sym
            return result

    @contract(figure_name='str')
    def remove_figure_symbols(self, figure_name: str):
        """
        Remove all symbols for given figure.

        Parameters
        ----------
        figure_name: str
            Name of figure.

        Raises
        -------
        IncorrectParamValue: if there is no figure with such name.
        """
        if figure_name not in self._figures_names:
            raise IncorrectParamValue(f'Figure {figure_name} does not exist.')

        symbols_to_delete = [
            name for name in self._symbols.keys()
            if split_full_name(name)[0] == figure_name
        ]

        for symbol_name in symbols_to_delete:
            self._symbols.pop(symbol_name)
        self._update_graph()

    @contract(restriction_name='str', equations='list')
    def add_restriction_equations(self, restriction_name: str,
                                  equations: list):
        """
        Add equations for one restriction.

        Parameters
        ----------
        restriction_name: str

        equations: list[sympy.Eq]
            List of equations.

        Raises
        ------
        IncorrectParamValue: if given restriction has already exist.
        """
        if restriction_name in self._restrictions_names:
            raise IncorrectParamValue(
                f'Restriction {restriction_name} has already exist.')

        equations_names = [compose_full_name(restriction_name, str(i))
                           for i in range(len(equations))]
        new_equations = {name: eq
                         for name, eq in zip(equations_names, equations)}
        self._equations.update(new_equations)
        self._update_graph()

    @contract(restriction_name='str')
    def remove_restriction_equations(self, restriction_name: str):
        """
        Remove all equations for given restriction.

        Parameters
        ----------
        restriction_name: str
            Name of restriction.

        Raises
        -------
        IncorrectParamValue: if there is no such restriction.
        """

        if restriction_name not in self._restrictions_names:
            raise IncorrectParamValue(
                f'Restriction {restriction_name} does not exists.')

        equations_to_delete = [
            name for name in self._equations.keys()
            if split_full_name(name)[0] == restriction_name
        ]

        for equation_name in equations_to_delete:
            self._equations.pop(equation_name)
        self._update_graph()

    @contract(current_values='figures_values', returns='figures_values')
    def solve(self, current_values: dict) -> dict:
        """Solve full system in a current state.

        Parameters
        ----------
        current_values: str -> (str -> number)
            Current values of variables: figure_name -> (symbol_name -> value).

        Returns
        ----------
        new_values: str -> (str -> number)
            New values of variables: figure_name -> (symbol_name -> value).
        """

        current_values = unroll_values_dict(current_values)

        result = {}
        subgraphs = [self._graph.subgraph(c).copy()
                     for c in nx.connected_components(self._graph)]
        for subgraph in subgraphs:
            equations_names = set([edge[2]['equation_name']
                                   for edge in subgraph.edges(data=True)])
            equations = [self._equations[name] for name in equations_names]

            symbols = {name: sym for name, sym in self._symbols.items()
                       if name in subgraph.nodes()}

            desired_values = {
                symbol_name: current_values[symbol_name]
                for symbol_name in symbols
            }

            res = self._solve_system(equations, symbols, desired_values)
            result.update(res)

        return roll_up_values_dict(result)

    @contract(new_equations='list[>0]', current_values='figures_values',
              returns='figures_values')
    def solve_new(self, new_equations: list, current_values: dict) -> dict:
        """Solve subsystem with new equation.

        Parameters
        ----------
        new_equations: list[sympy.Eq]
            New equations.
        current_values: str -> (str -> number)
            Current values of variables: figure_name -> (symbol_name -> value).

        Returns
        ----------
        new_values: str -> (str -> number)
            New values of variables: figure_name -> (symbol_name -> value).
        """

        current_values = unroll_values_dict(current_values)

        graph = self._graph.copy()
        for i, equation in enumerate(new_equations):
            name = compose_full_name(SPECIAL_NAME, str(i))
            self._add_equation_to_graph(graph, equation, equation_name=name)

        result = {}
        subgraphs = [graph.subgraph(c).copy()
                     for c in nx.connected_components(graph)]
        for subgraph in subgraphs:
            equations_in_subgraph_names = \
                set([e[2]['equation_name'] for e in subgraph.edges(data=True)])

            # Find equations in subgraph from new_equations
            new_equations_in_subgraph_names = []
            subgraph_equations = []
            for name in equations_in_subgraph_names:
                base_name, object_name = split_full_name(name)
                if base_name == SPECIAL_NAME:
                    new_equations_in_subgraph_names.append(name)
                    subgraph_equations.append(new_equations[int(object_name)])

            if not new_equations_in_subgraph_names:
                continue

            for name in new_equations_in_subgraph_names:
                equations_in_subgraph_names.remove(name)

            subgraph_equations.extend(
                [self._equations[name] for name in equations_in_subgraph_names]
            )

            symbols = {name: sym for name, sym in self._symbols.items()
                       if name in subgraph.nodes()}

            desired_values = {
                symbol_name: current_values[symbol_name]
                for symbol_name in symbols
            }

            result.update(self._solve_system(
                subgraph_equations, symbols, desired_values))

        return roll_up_values_dict(result)

    @measured
    @contract(optimizing_values='figures_values',
              current_values='figures_values', returns='figures_values')
    def solve_optimization_task(self, optimizing_values: dict,
                                current_values: dict) -> dict:
        """Solve subsystem with new equation.

        Parameters
        ----------
        optimizing_values: str -> (str -> number)
            Desired values of optimizing variables:
            figure_name -> (symbol_name -> value).
        current_values: str -> (str -> number)
            Current values of variables: figure_name -> (symbol_name -> value).

        Returns
        ----------
        new_values: str -> (str -> number)
            New values of variables: figure_name -> (symbol_name -> value).
        """

        optimizing_values = unroll_values_dict(optimizing_values)
        current_values = unroll_values_dict(current_values)

        result = dict()
        subgraphs = [self._graph.subgraph(c).copy()
                     for c in nx.connected_components(self._graph)]
        for subgraph in subgraphs:
            optimizing_values_in_subgraph = {
                symbol_name: value
                for symbol_name, value in optimizing_values.items()
                if symbol_name in subgraph.nodes()
            }

            if optimizing_values_in_subgraph:
                symbols = {name: sym for name, sym in self._symbols.items()
                           if name in subgraph.nodes()}
                desired_values = {
                    symbol_name: current_values[symbol_name]
                    for symbol_name in symbols
                }
                # desired_values.update(optimizing_values_in_subgraph)

                equations_names = set([edge[2]['equation_name']
                                       for edge in subgraph.edges(data=True)])
                equations = [self._equations[name] for name in equations_names]

                res = self._solve_optimization_task(equations, symbols,
                                                    desired_values, optimizing_values_in_subgraph)
                result.update(res)

        return roll_up_values_dict(result)

    @contract(system='list', symbols='dict(str: *)',
              desired_values='dict(str: float)', returns='dict(str: float)')
    def _solve_system(self, system: list, symbols: dict,
                      desired_values: dict) -> dict:

        if not system:  # no equations
            return {}

        if len(system) > len(symbols):
            raise MoreEquationsThanSymbolsError(
                f'System contains {len(system)} equations, but only '
                f'{len(symbols)} symbols.'
            )

        return self._solve_optimization_task(system, symbols, desired_values)

    @measured
    @contract(system='list[N]', symbols='dict[M], M >= N',
              desired_values='dict[M]', returns='dict[M]')
    def _solve_optimization_task(self, system: list, symbols: dict,
                                 desired_values: dict, high_priority_desired_values: dict = empty_dict) -> dict:
        assert set(symbols.keys()) == set(desired_values.keys()), \
            'symbols.keys() must be equal to best_values.keys()'

        # # Simplify by substitutions
        # substitutor = Substitutor()
        # try:
        #     with measure('substitutor fit'):
        #         substitutor.fit(system, symbols)
        # except SubstitutionError as e:
        #     raise CannotSolveSystemError(f'{type(e)}: {e.args}')
        #
        # with measure('substitutor sub'):
        #     simplified_system = substitutor.sub(system)
        # print(context_total.get_times())
        #
        # # Check easy inconsistency
        # if sympy_false in simplified_system:
        #     raise SystemIncompatibleError('Get BooleanFalse in system.')
        #
        # # Check easy inconsistency
        # if sympy_true in simplified_system:
        #     raise SystemOverfittedError('Get BooleanTrue in system.')
        #
        # system = simplified_system

        # ############################################################
        if len(system) == len(symbols):  # Optimization
            result = self._solve_square_system(system, symbols, desired_values)
            result = {name: value for name, value in result.items()}
            # result = substitutor.restore(result)
            return result

        lambdas_names = [compose_full_name('lambda', str(i))
                         for i in range(len(system))]
        lambdas_dict = {name: Symbol(name)  # TODO: real=True
                        for name in lambdas_names}
        lambdas = lambdas_dict.values()

        # Loss function: F = 1/2 * sum((xi - xi0) ** 2) + sum(lambda_j * eqj)
        # Derivatives by xi: dF/dxi = (xi - xi0) + d(sum(lambda_j * eqj)) / dxi
        # Derivatives by lambda_j: dF/d lambda_j = eqj (source system)

        canonical = self._system_to_canonical(system)
        loss_part2 = sum([l_j * canonical[j] for j, l_j in enumerate(lambdas)])
        if loss_part2 == 0:  # System is empty -> no lambdas
            loss_part2 = sympy_Integer(0)  # To be possible to diff

        # for sub_sym in substitutor.subs.keys():
        #     symbols.pop(sub_sym)

        with measure('get equations with diff'):
            equations = [0] * len(symbols)
            for i, (name, sym) in enumerate(symbols.items()):
                if name in high_priority_desired_values:
                    eq = Eq(BIG_NUMBER * (sym - high_priority_desired_values[name]) + loss_part2.diff(sym), 0)
                else:
                    eq = Eq(sym - desired_values[name] + loss_part2.diff(sym), 0)
                equations[i] = eq

        equations.extend(system)
        lambdas_dict.update(symbols)
        result = self._solve_square_system(equations, lambdas_dict,
                                           desired_values)

        result = {name: value for name, value in result.items()
                  if split_full_name(name)[0] != 'lambda'}
        # result = substitutor.restore(result)
        return result

    @classmethod
    @measured
    @contract(system='list[N]', symbols_dict='dict[N]',
              desired_values='dict | None', returns='dict[N]')
    def _solve_square_system(cls, system: list, symbols_dict: dict,
                             desired_values: dict = None):
        """Desired values only for setting initial conditions."""

        if len(symbols_dict) != len(system):
            raise RuntimeError(
                f'len(symbols_dict) = {len(symbols_dict)},'
                f'len(simplified_system) = {len(system)}'
            )

        symbols_names = list(symbols_dict.keys())
        symbols_list = [symbols_dict[name] for name in symbols_names]

        if system:
            # Prepare
            canonical_system = cls._system_to_canonical(system)
            system_function = \
                cls._system_to_function(canonical_system, symbols_list)

            # Prepare ini values
            ini_values = list(random.random(len(symbols_list)))
            if desired_values is not None:
                for i, symbol_name in enumerate(symbols_names):
                    if symbol_name in desired_values:
                        ini_values[i] = desired_values[symbol_name]

            # Solve
            solution = cls._solve_numeric(
                system_function, np_array(ini_values))
        else:
            solution = []

        # Add values for symbols that were substituted
        solution_dict = dict(zip(symbols_names, solution))

        return solution_dict

    @staticmethod
    @measured
    @contract(system='list[N,>0]', symbols='list[N]')
    def _system_to_function(system: list, symbols: list):
        functions = [lambdify(symbols, f, dummify=False) for f in system]

        def fun(x):
            if len(x) != len(symbols):
                raise ValueError
            res = np_array([f(*x) for f in functions])
            return res

        return fun

    @staticmethod
    @measured
    @contract(system='list')
    def _system_to_canonical(system: list):
        return [eq.lhs - eq.rhs for eq in system]

    @staticmethod
    @measured
    def _solve_numeric(fun: callable, init: np_ndarray) -> np_ndarray:
        result = sp_optimize.fsolve(fun, init, full_output=True, maxfev=1000)
        if result[2] != 1:
            raise CannotSolveSystemError(result[3])
        res = result[0]

        # result = sp_optimize.root(fun, init)
        # if not result.success:
        #     raise CannotSolveSystemError(result.message)
        # res = result.x

        return res

    def _update_graph(self):
        graph = nx.MultiGraph()
        graph.add_nodes_from(self._symbols)
        for eq_name, eq in self._equations.items():
            self._add_equation_to_graph(graph, eq, equation_name=eq_name)
        self._graph = graph

    @staticmethod
    @contract(equation_name='str | None', returns='None')
    def _add_equation_to_graph(graph, equation, equation_name=None):
        """Add edges to graph inplace."""
        eq_symbols = get_equation_symbols_names(equation, list(graph.nodes))

        if len(eq_symbols) == 0:
            raise RuntimeError(f'No symbols in equation {equation}.')
        elif len(eq_symbols) == 1:  # Equation like `Eq(figure1_x1, 5)`
            new_node_name = compose_full_name(GROWTH_NODE_NAME, equation_name)
            graph.add_node(new_node_name)
            graph.add_edge(new_node_name, eq_symbols.pop(),
                           equation_name=equation_name)
        else:
            for u, v in combinations(eq_symbols, 2):
                graph.add_edge(u, v, equation_name=equation_name)
