from contracts import contract
import math

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


class Coordinates:
    """Class of coordinates.

    Parameters
    ----------
    coordinates: tuple or function
        If tuple, it must be coordinates of point.
        If function, it must be function, that returns coordinates of point.
    """

    def __init__(self, coordinates, allow_none=False):
        super().__init__()
        if isinstance(coordinates, tuple):
            validate_coordinates(coordinates,
                                 'If coordinates is tuple, it must contain '
                                 '2 numbers.')

        elif callable(coordinates):
            test_coordinates = coordinates()
            if test_coordinates is not None or not allow_none:
                validate_coordinates(test_coordinates,
                                     'If coordinates is function, it must '
                                     'returns tuple that contains 2 numbers.')

        else:
            raise IncorrectParamType('Coordinates must be tuple or function.')

        self._coordinates = coordinates

    def get(self):
        """Return coordinates.

        Returns
        -------
        x, y: int or float
        """
        if isinstance(self._coordinates, tuple):
            return self._coordinates
        else:
            return self._coordinates()


def segment_length(x1, y1, x2, y2):
    magnitude_sqr = (x2 - x1) ** 2 + (y2 - y1) ** 2
    return magnitude_sqr ** 0.5


def segment_angle(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0:
        angle = math.pi / 2 if dy > 0 else -math.pi / 2
    elif dx > 0:
        angle = math.atan(dy / dx)
    else:
        angle = math.atan(dy / dx) + math.pi
    return angle


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


class ReferencedToObject:
    """Interface for objects that are referenced to other object"""

    def __init__(self):
        self._object_name = None

    @contract(object_name='str')
    def set_object_name(self, object_name: str):
        """Set host object name."""
        self._object_name = object_name

    @contract(returns='str')
    def get_object_name(self) -> str:
        """Get host object name."""
        return self._object_name


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
