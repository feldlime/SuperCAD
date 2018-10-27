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
    if not isinstance(coordinates, tuple) \
            or len(coordinates) != 2 \
            or not (isinstance(coordinates[0], int) or
                    isinstance(coordinates[0], float)) \
            or not (isinstance(coordinates[1], int) or
                    isinstance(coordinates[1], float)):
        raise IncorrectParamError(msg)


class Coordinates:
    """Class of coordinates.

    Parameters
    ----------
    coordinates: tuple or function
        If tuple, it must be coordinates of point.
        If function, it must be function, that returns coordinates of point.
    """

    def __init__(self, coordinates):
        super().__init__()
        if isinstance(coordinates, tuple):
            validate_coordinates(coordinates,
                                 'If coordinates is tuple, it must contain '
                                 '2 numbers.')

        elif callable(coordinates):
            test_coordinates = coordinates()
            validate_coordinates(test_coordinates,
                                 'If coordinates is function, it must returns'
                                 'tuple that contains 2 numbers.')

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


def magnitude(x1, y1, x2, y2):
    magnitude_sqr = (x2 - x1) ** 2 + (y2 - y1) ** 2
    return magnitude_sqr ** 0.5


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

    def clear(self):
        self._arr = []

    def __len__(self):
        return len(self._arr)

