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
        Pair of coordinates for base point of figure.
    angle: int or float, optional, default 0
        Angle (in radians) of rotation of figure with response to Ox.
    """

    def __init__(self, base=(0, 0), angle=0, **kwargs):
        if not isinstance(base, tuple)\
          or len(base) != 2\
          or not (isinstance(base[0], int) or isinstance(base[0], float))\
          or not (isinstance(base[1], int) or isinstance(base[1], float)):
            raise IncorrectParamType('Incorrect type of base')

        if not (isinstance(angle, int) or isinstance(angle, float)):
            raise IncorrectParamType('Incorrect type of angle')

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
        if not (isinstance(dx, int) or isinstance(dx, float)):
            raise IncorrectParamType('Incorrect type of dx')
        if not (isinstance(dy, int) or isinstance(dy, float)):
            raise IncorrectParamType('Incorrect type of dy')
        self._base += (dx, dy)
        return self

    def rotate(self, angle):
        """Move figure.

        Parameters
        ----------
        angle: int or float
            Angle to rotate figure.

        Return
        ------
         self
        """
        if not (isinstance(angle, int) or isinstance(angle, float)):
            raise IncorrectParamType('Incorrect type of angle')
        self._angle += angle
        return self

    def get_base_representation(self):
        """Return special representation of figure that not contains angles."""
        raise NotImplementedError

    @staticmethod
    def _simplify_angle(angle):
        return angle % (2 * np.pi)

    @staticmethod
    def _validate_positive(value, parameter_name):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise IncorrectParamError(f'Incorrect type of {parameter_name}')
        if value <= 0:
            raise IncorrectParamError(f'{parameter_name.capitalize()} '
                                      f'must be positive')


class Point(Figure):
    """Class of point.

    Parameters
    ----------
    base: tuple, optional, default (0, 0)
        Pair of coordinates for base point of figure.
    """
    def __init__(self, base=(0, 0)):
        super().__init__(base=base)

    def rotate(self, angle):
        raise NotImplementedError

    def get_base_representation(self):
        """Return special representation of figure that not contains angles.

        Return
        ------
        x, y: float
        """
        return self._base

    @classmethod
    def from_coordinates(cls, coordinates=(0, 0)):
        """Creates point from its coordinates.

        Parameters
        ----------
        coordinates: tuple, optional, default 0
            Coordinates (x, y) of point.

        Return
        ------
        point: Point
        """
        return cls(base=coordinates)


class Segment(Figure):
    """Class of segment.

    Parameters
    ----------
    base: tuple, optional, default (0, 0)
        Pair of coordinates for start point of segment.
    angle: int or float, optional, default 0
        Angle (in radians) between segment and Ox.
    length: int or float, optional, default 1
        Length of segment.
    """
    def __init__(self, base=(0, 0), angle=0, length=1):
        super().__init__(base, angle)
        self._validate_positive(length, 'length')
        self._i_length = float(length)

    @property
    def _length(self):
        return self._i_length

    @_length.setter
    def _length(self, value):
        self._validate_positive(value, 'length')
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


class Circle(Figure):
    """Class of circle.

    Parameters
    ----------
    center: tuple, optional, default (0, 0)
        Pair of coordinates for circle center.
    radius: int or float, optional, default 1
        Radius of circle.
    """
    def __init__(self, center=(0, 0), radius=1):
        super().__init__(base=center)
        self._validate_positive(radius, 'radius')
        self._i_radius = float(radius)

    @property
    def _radius(self):
        return self._i_radius

    @_radius.setter
    def _radius(self, value):
        self._validate_positive(value, 'radius')
        self._i_radius = float(value)

    def rotate(self, angle):
        raise NotImplementedError

    def get_base_representation(self):
        """Return special representation of figure that not contains angles.

        Return
        ------
        x_center, y_center, radius: float
        """
        return self._base[0], self._base[1], self._radius


class Arc(Figure):
    """Class of arc.

    Parameters
    ----------
    center: tuple, optional, default (0, 0)
        Pair of coordinates for arc center.
    radius: int or float, optional, default 1
        Radius of arc.
    center_angle: int or float, optional, default np.pi
        Angle (in radians) of spread. Must be > 0 and < 2*pi.
    angle: int or float, optional, default 0.
        Angle (in radians) between one of the ends and Ox.
    """
    def __init__(self, center=(0, 0), radius=1, center_angle=np.pi, angle=0):
        super().__init__(base=center, angle=angle)

        self._validate_positive(radius, 'radius')
        self._i_radius = float(radius)

        self._validate_center_angle(center_angle)
        self._i_center_angle = center_angle

    @property
    def _radius(self):
        return self._i_radius

    @_radius.setter
    def _radius(self, value):
        self._validate_positive(value, 'radius')
        self._i_radius = float(value)

    @property
    def _center_angle(self):
        return self._i_center_angle

    @_center_angle.setter
    def _center_angle(self, value):
        self._validate_center_angle(value)
        self._i_center_angle = float(value)

    def get_base_representation(self):
        """Return special representation of figure that not contains angles.

        Return
        ------
        x_center, y_center, radius: float
        """
        return self._base[0], self._base[1], self._radius

    @classmethod
    def _validate_center_angle(cls, angle):
        cls._validate_positive(angle, 'center angle')
        if angle >= 2 * np.pi:
            raise IncorrectParamError('Parameter  '
                                      'must be positive')
