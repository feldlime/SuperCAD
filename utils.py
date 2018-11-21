from contracts import contract
import numpy as np

BIG_DISTANCE = 10000


class IncorrectParamError(Exception):
    pass


class IncorrectParamType(IncorrectParamError, TypeError):
    pass


class IncorrectParamValue(IncorrectParamError, ValueError):
    pass


def validate_num(value, parameter_name):
    if not (isinstance(value, int) or isinstance(value, float)):
        raise IncorrectParamType(f'Incorrect type of {parameter_name}')


def validate_positive_num(value, parameter_name):
    validate_num(value, parameter_name)
    if value <= 0:
        raise IncorrectParamValue(f'{parameter_name.capitalize()} '
                                  f'must be positive')


def validate_coordinates(coordinates, msg):
    if not isinstance(coordinates, tuple):
        raise IncorrectParamType(msg)

    if len(coordinates) != 2 \
        or not (isinstance(coordinates[0], int) or
                isinstance(coordinates[0], float)) \
        or not (isinstance(coordinates[1], int) or
                isinstance(coordinates[1], float)):
        raise IncorrectParamValue(msg)


def segment_length(x1, y1, x2, y2):
    magnitude_sqr = (x2 - x1) ** 2 + (y2 - y1) ** 2
    return magnitude_sqr ** 0.5


def simplify_angle(angle):
    return angle % (2 * np.pi)


def segment_angle(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0:
        if dy == 0:
            return np.nan
        angle = np.pi / 2 if dy > 0 else -np.pi / 2
    elif dx > 0:
        angle = np.arctan(dy / dx)
    else:
        angle = np.arctan(dy / dx) + np.pi

    return simplify_angle(angle)


class EmptyStackError(Exception):
    pass


class Stack:
    def __init__(self):
        self._arr = []

    def push(self, elem):
        self._arr.append(elem)

    def pop(self):
        if self._arr:
            return self._arr.pop()
        else:
            raise EmptyStackError

    def get_head(self):
        if self._arr:
            return self._arr[-1]
        else:
            raise EmptyStackError

    def clear(self):
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

    @contract(returns='list(str)')
    def get_object_names(self) -> list:
        """Get host object name."""
        return self._object_names
