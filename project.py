"""Module with main class of system (backend)."""


class CADProject:
    def __init__(self):
        self._history = ChangesStack()  # All changes (for undo and rede)

    def add_figure(self):
        pass

    def add_restriction(self):
        pass

    def change_figure(self, figure, change):
        pass

    def move_figure(self, figure, coord):
        pass

    def get_updates(self):
        """Return all changes from changes stack."""
        pass

    def get_all(self):
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
