from contracts import contract
import numpy as np

BIG_DISTANCE = 10000


class IncorrectParamError(Exception):
    pass


class IncorrectParamType(IncorrectParamError, TypeError):
    pass


class IncorrectParamValue(IncorrectParamError, ValueError):
    pass


@contract(x1='number', y1='number', x2='number', y2='number')
def segment_length(x1, y1, x2, y2):
    """Calculate length of segment, represented by coordinates of its ends."""
    magnitude_sqr = (x2 - x1) ** 2 + (y2 - y1) ** 2
    return magnitude_sqr ** 0.5


@contract(angle='number')
def simplify_angle(angle):
    """Return equal angle to given, but in range [0, 2*pi]."""
    return angle % (2 * np.pi)


@contract(x1='number', y1='number', x2='number', y2='number')
def segment_angle(x1, y1, x2, y2):
    """Return angle of segment in range [0, 2*pi]."""
    dx, dy = x2 - x1, y2 - y1
    if dx == 0:
        if dy == 0:
            return 0
        angle = np.pi / 2 if dy > 0 else -np.pi / 2
    elif dx > 0:
        angle = np.arctan(dy / dx)
    else:
        angle = np.arctan(dy / dx) + np.pi

    return simplify_angle(angle)


class EmptyStackError(Exception):
    pass


class Stack:
    """Simple stack.

    Raises
    ------
    EmptyStackError: when try to see or pop elements of empty stack.
    """
    def __init__(self):
        self._arr = []

    def push(self, elem):
        """Put element to the head of stack."""
        self._arr.append(elem)

    def pop(self):
        """Take element from the head of stack."""
        if self._arr:
            return self._arr.pop()
        else:
            raise EmptyStackError

    def get_head(self):
        """Return (but not delete_ element that is on the head of stack."""
        if self._arr:
            return self._arr[-1]
        else:
            raise EmptyStackError

    def clear(self):
        """Delete all elements from stack."""
        self._arr = []

    def __len__(self):
        return len(self._arr)


class ReferencedToObjects:
    """Interface for objects that are referenced to other object"""
    _n_objects = None

    def __init__(self):
        self._object_names = None

    @contract(object_names='list(str)')
    def set_object_names(self, object_names: list):
        """Set host object name."""
        if self._n_objects is not None:
            if len(object_names) != self._n_objects:
                raise ValueError(
                    f'Len of object_names must be {self._n_objects}')
            self._object_names = object_names
        else:
            raise RuntimeError('self._objects_names is None.')

    @contract(returns='list(str)')
    def get_object_names(self) -> list:
        """Get host object names."""
        return self._object_names
