"""Module with main class of system (backend)."""

from figures import Figure, Point, Segment
from restrictions import Restriction


class CADProject:
    def __init__(self):
        self._history = ChangesStack()  # All changes (for undo and redo)
        self._figures = dict()
        self._restrictions = dict()

    def add_figure(self, figure: Figure, name: str = None):
        pass

    def change_figure(self, figure_name: str, parameter: str, value):
        pass

    def move_figure(self, figure_name: str, cursor_x, cursor_y):
        pass

    def remove_figure(self, figure_name: str):
        pass

    def add_restriction(self, restriction: Restriction, figure_names,
                        name: str = None):
        """
        """
        pass

    def remove_restriction(self, restriction_name):
        pass

    def get_state(self):
        """Return current state of system."""
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
