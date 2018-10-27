"""Module with main class of system (backend)."""

from contracts import contract
import pickle

from figures import Figure, Point, Segment
from bindings import (
    Binding,
    CentralBinding,
    SegmentStartBinding,
    SegmentEndBinding,
    SegmentCenterBinding,
    PointBinding
)
from restrictions import Restriction
from solve import EquationsSystem
from utils import (
    IncorrectParamError,
    IncorrectParamType,
    IncorrectParamValue
)


class IncorrectName(IncorrectParamValue):
    pass


class IncorrectUserName(IncorrectName):
    pass


class IncorrectTypeOfLoadedObject(Exception):
    pass


class ProjectState:
    def __init__(self):
        self.figures = dict()
        self.bindings = []
        self.restrictions = dict()
        self.system = EquationsSystem()


class CADProject:
    def __init__(self):
        self._state = ProjectState()
        self._history = ChangesStack()  # All changes (for undo and redo)

    @property
    def _figures(self):
        return self._state.figures

    @property
    def _bindings(self):
        return self._state.bindings

    @property
    def _restrictions(self):
        return self._state.restrictions

    @property
    def _system(self):
        return self._state.system

    @contract(figure='$Point|$Segment', name='str|None')
    def add_figure(self, figure: Figure, name: str = None):
        """Add figure to system.

        Parameters
        ----------
        figure: Figure instance
            Figure to add. Must be already created with correct parameters.
        name: str or None, optional, default None
            Name of figure. If None or empty, will be generated automatically.
        """
        if name is not None:
            if not self._is_valid_user_name(figure, name):
                raise IncorrectUserName
        else:
            name = self._generate_name(figure)
        if self._is_name_exists('figure', name):
            raise IncorrectName(f'Name {name} is already exists.')

        # TODO: Add bindings
        self._figures[name] = figure
        self._commit()

    @contract(figure_name='str', parameter='str', value='number')
    def change_figure(self, figure_name: str, parameter: str, value: float):
        """Change one parameter of one figure.

        Parameters
        ----------
        figure_name: str
            Name of figure to change.
        parameter: str
            Name of parameter to change.
        value: int or float
            New value for parameter.
        """

        if figure_name not in self._figures:
            raise IncorrectParamValue(f'Invalid figure_name {figure_name}')

        # TODO: Check that parameter is valid
        # TODO: Change
        # TODO: Update system
        self._commit()

    @contract(cursor_x='number', cursor_y='number')
    def move_figure(self, binding: CentralBinding,
                    cursor_x: float, cursor_y: float):
        """Move figure.

        Parameters
        ----------
        binding: CentralBinding instance
            Binding that was moved.
        cursor_x, cursor_y: int or float
            Coordinates of cursor.
        """
        if not (
            isinstance(binding, SegmentStartBinding)
            or isinstance(binding, SegmentEndBinding)
            or isinstance(binding, SegmentCenterBinding)
            or isinstance(binding, PointBinding)
        ):
            raise IncorrectParamType
        # TODO: Check figures names
        # TODO: Make all
        # TODO: Update system
        self._commit()

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

        self._figures.pop(figure_name)
        # TODO: Remove bindings
        # TODO: Remove restrictions
        self._commit()

    @contract(figure_names='tuple(str) | tuple(str,str)', name='str|None')
    def add_restriction(self, restriction: Restriction, figure_names: tuple,
                        name: str = None):
        """Add restriction to system.

        Parameters
        ----------
        restriction: Restriction instance
            Restriction to add. Must be object of correct class with correct
            parameters.
        figure_names: tuple
            Names of figures to apply restriction. If figure is only one,
            must be a tuple of one element.
        name: str or None, optional, default None
            Name of restriction. If None or empty, will be generated
            automatically.
        """
        if not isinstance(restriction, Restriction):
            raise IncorrectParamType

        if name is not None:
            if not self._is_valid_user_name(restriction, name):
                raise IncorrectUserName
        else:
            name = self._generate_name(restriction)
        if self._is_name_exists('restriction', name):
            raise IncorrectName(f'Name {name} is already exists.')

        for figure_name in figure_names:
            if figure_name not in self._figures:
                raise IncorrectParamValue(f'Invalid figure_name {figure_name}')

        # TODO: Check that this restriction requires this number and types of
        # TODO: figures

        # TODO: Make all
        # TODO: Update system
        self._commit()

    @contract(restriction_name='str')
    def remove_restriction(self, restriction_name: str):
        """Remove restriction.

        Parameters
        ----------
        restriction_name: str
            Name of restriction to remove.
        """
        if restriction_name not in self._restrictions:
            raise IncorrectParamValue(f'Invalid restriction_name'
                                      f' {restriction_name}')

        self._restrictions.pop(restriction_name)
        # TODO: Update system
        self._commit()

    @contract(returns='dict')
    def get_figures(self) -> dict:
        """Get dictionary of figures.

        Returns
        -------
        figures: dict
            Keys are figures names, values are Figure instances.
        """
        return dict(self._figures)

    @contract(returns='list')
    def get_bindings(self) -> list:
        """Get list of bindings.

        Returns
        -------
        bindings: list
        """
        return list(self._bindings)

    @contract(returns='dict')
    def get_restrictions(self) -> dict:
        """Get dictionary of restrictions.

        Returns
        -------
        restrictions: dict
            Keys are restrictions names, values are Restriction instances.
        """
        return dict(self._restrictions)

    def undo(self):
        """Cancel action"""
        pass

    def redo(self):
        """Revert action"""
        pass

    @contract(filename='str')
    def save(self, filename: str):
        """Save system state to .pkl file.

        Parameters
        ----------
        filename: str
            Name of file to save (without extension).
        """
        filename = filename + '.pkl'
        with open(filename, 'wb') as f:
            pickle.dump(self._state, f)

    @contract(filename='str')
    def load(self, filename: str):
        """Load system state from file.

        Parameters
        ----------
        filename: str
            Name of file to load.
            Extension must be .pkl.
        """
        if not filename.endswith('.pkl'):
            raise IncorrectParamValue('File must have .pkl extension.')

        with open(filename, 'rb') as f:
            state = pickle.load(f)

        if not isinstance(state, ProjectState):
            raise IncorrectTypeOfLoadedObject

        self._state = state
        self._history = ChangesStack()

    def _generate_name(self, obj) -> str:
        """Generate new names for figures and bindings"""
        type_str = str(type(obj))

        if isinstance(obj, Figure):
            names_list = list(self._figures.keys())
        elif isinstance(obj, Restriction):
            names_list = list(self._restrictions.keys())
        else:
            raise ValueError(f'Incorrect obj type {type_str}')

        nums = [int(name.split('_')[-1])
                for name in names_list if name.startswith(type_str)]

        name = f'{type_str}_{max(nums) + 1}'
        return name

    @staticmethod
    @contract(name='str')
    def _is_valid_user_name(obj, name: str):
        """Check if name that was given by user is valid"""
        if not name:
            return False

        type_str = str(type(obj))
        return not name.startswith(type_str)

    @contract(type_='str', name='str')
    def _is_name_exists(self, type_: str, name: str):
        if type_ == 'figure':
            return name in self._figures.keys()
        elif type_ == 'restriction':
            return name in self._restrictions.keys()
        else:
            raise ValueError(f'Incorrect type_ {type_}')

    def _commit(self):
        """Save current state to history."""
        self._history.push(self._state)


class EmptyStackError(Exception):
    pass


class Stack:
    def __init__(self):
        self._arr = []

    def push(self, elem):
        self._arr.append(elem)

    def pop(self):
        try:
            return self._arr.pop()
        except IndexError:
            raise EmptyStackError


class ChangesStack(Stack):
    pass
