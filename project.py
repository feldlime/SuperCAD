"""Module with main class of system (backend)."""

from figures import Figure, Point, Segment
from bindings import (
    Binding,
    CentralBinding,
)
from restrictions import Restriction
from solve import EquationsSystem

from contracts import contract


class CADProject:
    def __init__(self):
        self._history = ChangesStack()  # All changes (for undo and redo)
        self._figures = dict()
        self._bindings = []
        self._restrictions = dict()
        self._system = EquationsSystem()

    @contract(figure='Figure', name='str')
    def add_figure(self, figure: Figure, name: str = None):
        """Add figure to system.

        Parameters
        ----------
        figure: Figure instance
            Figure to add. Must be already created with correct parameters.
        name: str or None, optional, default None
            Name of figure. If None or empty, will be generated automatically.
        """

        name = name or self._generate_name()

    @contract(figure_name='str', parameter='str', value='int|float')
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

        pass

    @contract(figure_name='CentralBinding', cursor_x='int|float',
              cursor_y='int|float')
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
        pass

    @contract(figure_name='str')
    def remove_figure(self, figure_name: str):
        """Remove figure.

        Parameters
        ----------
        figure_name: str
            Name of figure to remove.
        """

        pass

    @contract(restriction='Restriction', figure_names='tuple')
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
        pass

    @contract(restriction_name='str')
    def remove_restriction(self, restriction_name: str):
        """Remove restriction.

        Parameters
        ----------
        restriction_name: str
            Name of restriction to remove.
        """
        pass

    @contract(returns='dict')
    def get_figures(self) -> dict:
        """Get dictionary of figures.

        Returns
        -------
        figures: dict
            Keys are figures names, values are Figure instances.
        """
        pass

    @contract(returns='list')
    def get_bindings(self) -> list:
        pass

    @contract(returns='dict')
    def get_restrictions(self) -> dict:
        """Get dictionary of restrictions.

        Returns
        -------
        restrictions: dict
            Keys are restrictions names, values are Restriction instances.
        """
        pass

    def undo(self):
        """Cancel action"""
        pass

    def redo(self):
        """Revert action"""
        pass

    @contract(filename='str')
    def save(self, filename: str):
        """Save system state to file.

        Parameters
        ----------
        filename: str
            Name of file to save.
        """
        pass

    @contract(filename='str')
    def load(self, filename: str):
        """Load system state from file.

        Parameters
        ----------
        filename: str
            Name of file to load.
        """
        pass

    def _generate_name(self, obj) -> str:
        """Generate new names for figures and bindings"""
        count = 0
        type_ = type(obj)

        if isinstance(obj, Figure):
            for figure in self._figures.values():
                if type(figure) is type_:
                    count += 1
        elif isinstance(obj, Restriction):
            for restriction in self._restrictions.values():
                if type(restriction) is type_:
                    count += 1
        else:
            raise ValueError(f'Incorrect obj type {type_}')

        name = f'{type_}_{count + 1}'
        return name

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
