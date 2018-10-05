import numpy as np


class IncorrectParamError(Exception):
    pass


class Figure:
    def __init__(self, base=(0, 0), angle=0, **kwargs):
        self._base = base
        self._i_angle = self._simplify_angle(angle)

    @property
    def _angle(self):
        return self._i_angle

    @_angle.setter
    def _angle(self, value):
        self._i_angle = self._simplify_angle(value)

    def move(self, dx=0, dy=0):
        self._base += (dx, dy)

    def rotate(self, angle):
        self._angle += angle

    @staticmethod
    def _simplify_angle(angle):
        return angle % (2 * np.pi)

    @staticmethod
    def _validate_positive(value, parameter_name):
        if value <= 0:
            raise IncorrectParamError(f'Parameter {parameter_name} '
                                      f'must be positive')


class Point(Figure):
    def __init__(self, base=(0, 0), angle=0):
        super().__init__(base, angle)


class Segment(Figure):
    def __init__(self, base=(0, 0), angle=0, length=1):
        super().__init__(base, angle)
        self._validate_positive(length, 'length')
        self._i_length = length

    @property
    def _length(self):
        return self._i_length

    @_length.setter
    def _length(self, value):
        self._validate_positive(value, 'length')
        self._i_length = value


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

