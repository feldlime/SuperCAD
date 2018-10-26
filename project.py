"""Module with main class of system (backend)."""

from figures import Figure, Point, Segment
from bindings import Binding
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

    @contract(figure='Figure')
    def add_figure(self, figure: Figure, name: str = None):
        pass

    @contract(figure_name='str', parameter='str', value='int|float')
    def change_figure(self, figure_name: str, parameter: str, value: float):
        pass

    @contract(figure_name='str', cursor_x='int|float', cursor_y='int|float')
    def move_figure(self, figure_name: str, cursor_x: float, cursor_y: float):
        pass

    @contract(figure_name='str')
    def remove_figure(self, figure_name: str):
        pass

    @contract(restriction='Restriction', figure_names='tuple')
    def add_restriction(self, restriction: Restriction, figure_names: tuple,
                        name: str = None):
        """
        """
        pass

    @contract(restriction_name='str')
    def remove_restriction(self, restriction_name: str):
        pass

    @contract(returns='dict')
    def get_figures(self) -> dict:
        pass

    @contract(returns='list')
    def get_bindings(self) -> list:
        pass

    @contract(returns='dict')
    def get_restrictions(self) -> dict:
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    @contract(filename='str')
    def save(self, filename: str):
        pass

    @contract(filename='str')
    def load(self, filename: str):
        pass


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
