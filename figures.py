import numpy as np


class IncorrectParamError(Exception):
    pass


class IncorrectParamType(IncorrectParamError, TypeError):
    pass


class Figure:
    """Base class for any geometry figure.

    Parameters
    ----------
    base: tuple, optional, default (0, 0)
        Pair of coordinates (int or float) for base point of figure.
    angle: int or float, optional, default 0
        Angle (in radians) of rotation of figure with response to Ox.
    """

    def __init__(self, base=(0, 0), angle=0, **kwargs):
        if not isinstance(base, tuple)\
          or len(base) != 2\
          or not (isinstance(base[0], int) or isinstance(base[0], float))\
          or not (isinstance(base[1], int) or isinstance(base[1], float)):
            raise IncorrectParamType('Incorrect type of base')

        self._validate_num(angle, 'angle')

        self._base = (float(base[0]), float(base[1]))
        self._i_angle = self._simplify_angle(float(angle))

    @property
    def _angle(self):
        return self._i_angle

    @_angle.setter
    def _angle(self, value):
        self._i_angle = self._simplify_angle(float(value))

    def move(self, dx=0, dy=0):
        """Move figure.

        Parameters
        ----------
        dx: int or float
            Value to increase x.
        dy: int or float
            Value to increase y.

        Return
        ------
         self
        """
        self._validate_num(dx, 'dx')
        self._validate_num(dy, 'dy')
        self._base = self._base[0] + dx, self._base[1] + dy
        return self

    def rotate(self, angle):
        """Rotate figure.

        Parameters
        ----------
        angle: int or float
            Angle to rotate figure.

        Return
        ------
         self
        """
        self._validate_num(angle, 'angle')
        self._angle += angle
        return self

    def get_base_representation(self):
        """Return special representation of figure that not contains angles."""
        return NotImplemented

    @staticmethod
    def _simplify_angle(angle):
        return angle % (2 * np.pi)

    @staticmethod
    def _validate_num(value, parameter_name):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise IncorrectParamType(f'Incorrect type of {parameter_name}')

    @staticmethod
    def _validate_positive_num(value, parameter_name):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise IncorrectParamError(f'Incorrect type of {parameter_name}')
        if value <= 0:
            raise IncorrectParamError(f'{parameter_name.capitalize()} '
                                      f'must be positive')

    def __repr__(self):
        desc = f'{self.__class__.__name__} with base representation: ' \
               f'{self.get_base_representation()}'
        return desc


class Point(Figure):
    """Class of point.

    Parameters
    ----------
    coordinates: tuple, optional, default (0, 0)
        Pair of point coordinates (int or float).
    """
    def __init__(self, coordinates=(0, 0)):
        super().__init__(base=coordinates)

    def rotate(self, angle):
        """Not implemented here."""
        return NotImplemented

    def get_base_representation(self):
        """Return special representation of figure that not contains angles.

        Return
        ------
        x, y: float
        """
        return self._base

    @classmethod
    def from_coordinates(cls, x, y):
        """Creates point from its coordinates.

        Parameters
        ----------
        x: int or float
            Coordinate x of point.
        y: int or float
            Coordinate y of point.

        Return
        ------
        point: Point instance
        """
        cls._validate_num(x, 'x')
        cls._validate_num(y, 'y')
        return cls(coordinates=(x, y))


class Segment(Figure):
    """Class of segment.

    Parameters
    ----------
    start: tuple, optional, default (0, 0)
        Pair of coordinates for start point of segment.
    angle: int or float, optional, default 0
        Angle (in radians) between segment and Ox.
    length: int or float, optional, default 1
        Length of segment.
    """
    def __init__(self, start=(0, 0), angle=0, length=1):
        super().__init__(start, angle)
        self._validate_positive_num(length, 'length')
        self._i_length = float(length)

    @property
    def _length(self):
        return self._i_length

    @_length.setter
    def _length(self, value):
        self._validate_positive_num(value, 'length')
        self._i_length = float(value)

    def get_base_representation(self):
        """Return special representation of figure that not contains angles.

        Return
        ------
        x1, y1, x2, y2: float
        """
        x1, y1 = self._base
        x2 = x1 + self._length * np.cos(self._angle)
        y2 = y1 + self._length * np.sin(self._angle)
        return x1, y1, x2, y2

    @classmethod
    def from_points(cls, x1, y1, x2, y2):
        """Create segment from its end points.

        x1: int or float
            Coordinate x of the start of segment.
        y1: int or float
            Coordinate y of the end of segment.
        x2: int or float
            Coordinate x of the start of segment.
        y2: int or float
            Coordinate y of the end of segment.
        """
        cls._validate_num(x1, 'x1')
        cls._validate_num(y1, 'y1')
        cls._validate_num(x2, 'x2')
        cls._validate_num(y2, 'y2')

        dx, dy = x2 - x1, y2 - y1
        length = np.sqrt(dx ** 2 + dy ** 2)

        cls._validate_positive_num(length, 'length')

        if dx == 0:
            angle = np.pi / 2 if dy > 0 else -np.pi / 2
        elif dx > 0:
            angle = np.arctan(dy / dx)
        else:
            angle = np.arctan(dy / dx) + np.pi

        return cls(start=(x1, y1), angle=angle, length=length)
