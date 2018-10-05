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
        Angle (in radians) of rotation of figure.
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
            raise IncorrectParamError(f'Parameter {parameter_name} '
                                      f'must be positive')


class Point(Figure):
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

        """


class Segment(Figure):
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

        """

class Restriction:
    def get_restriction_equation(self, objects):
        # may be no objects
        pass


class FixedLength(Restriction):
    def __init__(self, length=None):
        """

        length:
            If None use current length.
        """
        self._length = length


# more


class FiguresAndRestrictionsSystem:
    def __init__(self):
        self._figures = {}
        self._restrictions = {}  # or list?

    def add_figure(self):
        pass

    def add_restriction(self, name, restriction, objects):
        # may be no name
        # restri
        pass

    def _check_if_restriction_possible(self):
        pass


figure = Figure()
figure.rotate(3)
figure.move(1, 2)

segment = Segment(length=-2)
