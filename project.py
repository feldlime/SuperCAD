"""Module with main class of system (backend)."""

from contracts import contract
from pickle import load as pkl_load, dump as pkl_dump
from copy import deepcopy
import numpy as np
from typing import Dict


from figures import Figure, Point, Segment
from bindings import (
    SegmentSpotBinding,
    PointBinding,
    FullSegmentBinding,
    create_bindings,
)
from restrictions import Restriction
from solve import EquationsSystem, CannotSolveSystemError
from utils import (
    IncorrectParamType,
    IncorrectParamValue,
    Stack,
    EmptyStackError,
)

from diagnostic_context import measured

CIRCLE_BINDING_RADIUS = 12
SEGMENT_BINDING_MARGIN = 6


class IncorrectName(IncorrectParamValue):
    pass


class IncorrectUserName(IncorrectName):
    pass


class IncorrectTypeOfLoadedObject(Exception):
    pass


class ActionImpossible(Exception):
    pass


class ProjectState:
    def __init__(self):
        self.figures = dict()
        self.restrictions = dict()

        # It's not necessary to save bindings and system to state
        # But it's done for convenience and speed
        self.bindings = []
        self.system = EquationsSystem()


class ChangesStack(Stack):
    pass


class CADProject:
    def __init__(self):
        self._state = ProjectState()
        self._history = ChangesStack()  # All changes (for undo)
        self._cancelled = ChangesStack()  # Cancelled changes (for redo)

        self._commit()

    @property
    def _figures(self):
        return self._state.figures

    @property
    def _bindings(self):
        return self._state.bindings

    @_bindings.setter
    def _bindings(self, value):
        self._state.bindings = value

    @property
    def _restrictions(self):
        return self._state.restrictions

    @property
    def _system(self):
        return self._state.system

    @property
    def figures(self):
        """Dictionary of figures."""
        return dict(self._figures)

    @property
    def bindings(self):
        """List of bindings."""
        return list(self._bindings)

    @property
    def restrictions(self):
        """Dictionary of restrictions."""
        return dict(self._restrictions)

    @contract(figure='$Point|$Segment', name='str|None')
    def add_figure(self, figure: Figure, name: str = None):
        """Add figure to system.

        Parameters
        ----------
        figure: Figure instance
            Figure to add. Must be already created with correct parameters.
        name: str or None, optional, default None
            Name of figure. If None or empty, will be generated automatically.

        Returns
        -------
        name: str
            Name that was given to figure.
        """
        if name is not None:
            if not self._is_valid_user_name(figure, name):
                raise IncorrectUserName
        else:
            name = self._generate_name(figure)
        if self._is_name_exists('figure', name):
            raise IncorrectName(f'Name {name} is already exists.')

        try:
            self._figures[name] = figure
            self._bindings = create_bindings(
                self._figures,
                circle_bindings_radius=CIRCLE_BINDING_RADIUS,
                segment_bindings_margin=SEGMENT_BINDING_MARGIN,
            )  # Slow but easy
            self._system.add_figure_symbols(name, figure.base_parameters)
        except:
            self._rollback()
            raise
        else:
            self._commit()

        return name

    @contract(figure_name='str', param='str', value='number')
    def change_figure(self, figure_name: str, param: str, value: float):
        """Change one parameter of one figure.

        Parameters
        ----------
        figure_name: str
            Name of figure to change.
        param: str
            Name of parameter to change.
        value: int or float
            New value for parameter.
        """

        if figure_name not in self._figures:
            raise IncorrectParamValue(f'Invalid figure_name {figure_name}')

        figure = self._figures[figure_name]
        if param not in figure.all_parameters:
            raise IncorrectParamValue(
                f'Parameter must be one of {figure.all_parameters}'
            )

        figure_symbols = self._system.get_symbols(figure_name)
        equations = figure.get_setter_equations(figure_symbols, param, value)

        current_values = self._get_values()
        try:
            new_values = self._system.solve_new(equations, current_values)
        except CannotSolveSystemError as e:
            raise e

        try:
            self._set_values(new_values)
        except Exception as e:
            self._rollback()
            raise e
        else:
            self._commit()

    @measured
    @contract(cursor_x='number', cursor_y='number')
    def move_figure(
        self, binding: PointBinding, cursor_x: float, cursor_y: float
    ):
        """Move figure.

        Parameters
        ----------
        binding: CentralBinding instance
            Binding that was moved.
        cursor_x, cursor_y: int or float
            Coordinates of cursor.
        """

        obj_name = binding.get_object_names()[0]
        if obj_name not in self._figures:
            raise RuntimeError(
                'Binding references to figure that does not exist.'
            )

        cursor_x, cursor_y = float(cursor_x), float(cursor_y)

        if isinstance(binding, PointBinding):
            optimizing_values = {obj_name: {'x': cursor_x, 'y': cursor_y}}
        elif isinstance(binding, SegmentSpotBinding):
            spot_type = binding.spot_type
            if spot_type == 'start':
                optimizing_values = {
                    obj_name: {'x1': cursor_x, 'y1': cursor_y}
                }
            elif spot_type == 'end':
                optimizing_values = {
                    obj_name: {'x2': cursor_x, 'y2': cursor_y}
                }
            else:  # center
                params = self._figures[obj_name].get_params()
                length, angle = params['length'], params['angle']
                optimizing_values = {
                    obj_name: {
                        'x1': cursor_x - length * np.cos(angle) / 2,
                        'y1': cursor_y - length * np.sin(angle) / 2,
                        'x2': cursor_x + length * np.cos(angle) / 2,
                        'y2': cursor_y + length * np.sin(angle) / 2,
                    }
                }
        elif isinstance(binding, FullSegmentBinding):
            return
        else:
            raise IncorrectParamType(f"Incorrect type {type(binding)}")

        current_values = self._get_values()
        try:
            new_values = self._system.solve_optimization_task(
                optimizing_values, current_values
            )
        except CannotSolveSystemError as e:
            raise e

        self._set_values(new_values)

    @contract(figure_name='str')
    def remove_figure(self, figure_name: str):
        """Remove figure.

        Parameters
        ----------
        figure_name: str
            Name of figure to remove.
        """
        if figure_name not in self._figures:
            raise IncorrectParamValue(f'Invalid figure_name {figure_name}')

        try:
            # Remove figure
            self._figures.pop(figure_name)

            # Remove bindings
            self._bindings = create_bindings(self._figures)  # Slow but easy

            # Remove restrictions
            restrictions_to_remove = []
            for name, restriction in self._restrictions.items():
                if figure_name in restriction.get_object_names():
                    restrictions_to_remove.append(name)
            for restriction_name in restrictions_to_remove:
                self._restrictions.pop(restriction_name)

            # Remove from system
            for restriction_name in restrictions_to_remove:
                self._system.remove_restriction_equations(restriction_name)
            self._system.remove_figure_symbols(figure_name)

        except:
            self._rollback()
            raise
        else:
            self._commit()

    @contract(figures_names='tuple(str) | tuple(str,str)', name='str|None')
    def add_restriction(
        self, restriction: Restriction, figures_names: tuple, name: str = None
    ):
        """Add restriction to system.

        Parameters
        ----------
        restriction: Restriction instance
            Restriction to add. Must be object of correct class with correct
            parameters.
        figures_names: tuple
            Names of figures to apply restriction. If figure is only one,
            must be a tuple of one element.
        name: str or None, optional, default None
            Name of restriction. If None or empty, will be generated
            automatically.
        """
        if not isinstance(restriction, Restriction):
            raise IncorrectParamType

        # Define restriction name
        if name is not None:
            if not self._is_valid_user_name(restriction, name):
                raise IncorrectUserName
        else:
            name = self._generate_name(restriction)
        if self._is_name_exists('restriction', name):
            raise IncorrectName(f'Name {name} is already exists.')

        # Check figures names
        for figure_name in figures_names:
            if figure_name not in self._figures:
                raise IncorrectParamValue(f'Invalid figure_name {figure_name}')

        # Check figures types
        types = restriction.object_types
        if len(figures_names) != len(types):
            raise IncorrectParamValue(f'Must be {len(types)} figures.')
        for figure_name, type_ in zip(figures_names, types):
            if not isinstance(self._figures[figure_name], type_):
                raise IncorrectParamValue(
                    f'Given figures must have types {types}'
                )

        # Add to system
        figures_symbols = [
            self._system.get_symbols(figure_name)
            for figure_name in figures_names
        ]
        equations = restriction.get_equations(*figures_symbols)

        current_values = self._get_values()

        try:
            self._system.add_restriction_equations(name, equations)

            # Try solve
            try:
                new_values = self._system.solve(current_values)
            except CannotSolveSystemError as e:
                # Remove from system
                self._system.remove_restriction_equations(name)
                raise e

            # Add
            restriction.set_object_names(list(figures_names))
            self._restrictions[name] = restriction

            # Update values
            self._set_values(new_values)

        except:
            self._rollback()
            raise
        else:
            self._commit()

        return name

    @contract(restriction_name='str')
    def remove_restriction(self, restriction_name: str):
        """Remove restriction.

        Parameters
        ----------
        restriction_name: str
            Name of restriction to remove.
        """
        if restriction_name not in self._restrictions:
            raise IncorrectParamValue(
                f'Invalid restriction_name' f' {restriction_name}'
            )

        try:
            self._restrictions.pop(restriction_name)
            self._system.remove_restriction_equations(restriction_name)

        except:
            self._rollback()
            raise
        else:
            self._commit()

    def undo(self):
        """Cancel action."""
        if len(self._history) > 1:
            self._history.pop()  # Current state (equal to self._state)
            self._cancelled.push(self._state)
            self._state = deepcopy(self._history.get_head())
        else:
            raise ActionImpossible

    def redo(self):
        """Revert action."""
        try:
            last_cancelled_state = self._cancelled.pop()
            self._history.push(deepcopy(last_cancelled_state))
            self._state = last_cancelled_state
        except EmptyStackError:
            raise ActionImpossible

    @contract(filename='str')
    def save(self, filename: str):
        """Save system state to .scad file.

        Parameters
        ----------
        filename: str
            Name of file to save (with extension).
        """
        with open(filename, 'wb') as f:
            pkl_dump(self._state, f)

    @contract(filename='str')
    def load(self, filename: str):
        """Load system state from .scad file.

        Parameters
        ----------
        filename: str
            Name of file to load.
        """
        with open(filename, 'rb') as f:
            state = pkl_load(f)

        if not isinstance(state, ProjectState):
            raise IncorrectTypeOfLoadedObject

        self._state = state
        self._history.clear()
        self._cancelled.clear()

    def commit(self):
        """Commit changes."""
        self._commit()

    def rollback(self):
        """Rollback changes."""
        self._rollback()

    def _generate_name(self, obj) -> str:
        """Generate new names for figures and bindings"""
        type_str = type(obj).__name__

        if isinstance(obj, Figure):
            names_list = list(self._figures.keys())
        elif isinstance(obj, Restriction):
            names_list = list(self._restrictions.keys())
        else:
            raise ValueError(f'Incorrect obj type {type_str}')

        nums = [
            int(name.split('_')[-1])
            for name in names_list
            if name.startswith(type_str)
        ]

        num = max(nums) + 1 if nums else 1
        name = f'{type_str}_{num}'
        return name

    @staticmethod
    @contract(name='str')
    def _is_valid_user_name(obj, name: str):
        """Check if name that was given by user is valid"""
        if not name:
            return False

        if name.startswith(type(obj).__name__):
            return False

        if len(name.split()) > 1:
            return False

        return True

    @contract(type_='str', name='str')
    def _is_name_exists(self, type_: str, name: str):
        if type_ == 'figure':
            return name in self._figures.keys()
        elif type_ == 'restriction':
            return name in self._restrictions.keys()
        else:
            raise ValueError(f'Incorrect type_ {type_}')

    def _get_values(self) -> Dict[str, Dict[str, float]]:
        """

        Returns
        -------
        current_values: dict(str -> dict(str -> float))
            figure_name -> (variable_name -> value)
        """
        values = dict()
        for name, figure in self._figures.items():
            repr_ = figure.get_base_representation()
            if isinstance(figure, Point):
                values[name] = dict(zip(['x', 'y'], repr_))
            elif isinstance(figure, Segment):
                values[name] = dict(zip(['x1', 'y1', 'x2', 'y2'], repr_))
            else:
                raise TypeError(f'Unexpected figure type {type(figure)}')
        return values

    def _set_values(self, values: Dict[str, Dict[str, float]]):
        """
        Parameters
        -------
        values: dict(str -> dict(str -> float))
            figure_name -> (variable_name -> value)
        """

        for figure_name, figure_values in values.items():
            if figure_name not in self._figures:
                raise ValueError(
                    f'Figure with name {figure_name} does not exist.'
                )

            for param_name, value in figure_values.items():
                self._figures[figure_name].set_base_param(param_name, value)

    def _commit(self):
        """Save current state to history."""
        self._history.push(deepcopy(self._state))
        self._cancelled.clear()

    def _rollback(self):
        """Load last state from history."""
        self._state = deepcopy(self._history.get_head())
        # self._cancelled.clear()  # ???
