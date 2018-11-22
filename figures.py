"""Module with classes of geometry figures."""

import numpy as np
import sympy
from contracts import contract

from utils import (
    IncorrectParamValue,
    segment_length,
    segment_angle,
    simplify_angle
)


class Figure:
    """Base class for any geometry figure.

    Parameters
    ----------
    base: tuple, optional, default (0, 0)
        Pair of coordinates (int or float) for base point of figure.
    angle: int or float, optional, default 0
        Angle (in radians) of rotation of figure with response to Ox.
    """
    all_parameters = ['base_x', 'base_y', 'angle']
    base_parameters = []

    @contract(base='tuple(number, number) | None', angle='number | None')
    def __init__(self, base=(0, 0), angle=0, **kwargs):
        self._base = (float(base[0]), float(base[1]))
        self._i_angle = simplify_angle(float(angle))

    @property
    def _angle(self):
        return self._i_angle

    @_angle.setter
    @contract(value='number')
    def _angle(self, value):
        self._i_angle = simplify_angle(float(value))

    @contract(dx='number | None', dy='number | None')
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
        self._base = self._base[0] + dx, self._base[1] + dy
        return self

    @contract(angle='number')
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
        self._angle += angle
        return self

    def get_base_representation(self):
        """Return special representation of figure that not contains angles."""
        return NotImplemented

    def get_params(self):
        """Return parameters of figure."""
        raise NotImplementedError

    def set_param(self, param_name, value):
        """Set parameter of figure."""
        raise NotImplementedError

    def get_setter_equations(self, symbols: list, param: str, value: float):
        raise NotImplementedError

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
    all_parameters = ['x', 'y']
    base_parameters = ['x', 'y']

    @contract(coordinates='tuple(number, number) | None')
    def __init__(self, coordinates=(0, 0)):
        super().__init__(base=coordinates)

    def rotate(self, angle):
        """Not implemented here."""
        return NotImplemented

    @contract(returns='tuple(float, float)')
    def get_base_representation(self):
        """Return special representation of figure that not contains angles.

        Return
        ------
        x, y: float
        """
        return self._base

    @classmethod
    @contract(x='number', y='number')
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
        return cls(coordinates=(x, y))

    @contract(returns='dict(str: float)')
    def get_params(self):
        """Return all parameters.

        Returns
        -------
        params: dict(str -> float)
            Keys are ['x', 'y'].
        """
        return {'x': self._base[0],
                'y': self._base[1]}

    @contract(param_name='str', value='number')
    def set_param(self, param_name, value):
        """Set parameter of figure.

        Parameters
        ----------
        param_name: str
            Name of parameter to set value.
            Must be in ['x', 'y'].
        value: int or float
            Value too set.

        Returns
        -------
        self

        Raises
        ------
        IncorrectParamValue: if param is incorrect.
        """

        if param_name == 'x':
            self._base = (float(value), self._base[1])
        elif param_name == 'y':
            self._base = (self._base[0], float(value))
        else:
            raise IncorrectParamValue(
                f'Incorrect name of parameter: {param_name}.')

        return self

    @contract(symbols='list[2]', param='str', value='number', returns='list')
    def get_setter_equations(self, symbols: list, param: str, value: float):
        """Return equations for setting parameters of point.

        Parameters
        ----------
        symbols: list[sympy.Symbol]
            Symbols for segment.
            Must contain 2 elements: symbols for x, y.
        param: str
            Name of parameter to set value.
            Must be in ['x', 'y'].
        value: int or float
            Value to set.

        Returns
        -------
        equations: list[sympy.Eq]
            List of equations.

        Raises
        ------
        IncorrectParamValue: if param is incorrect.
        """
        x, y = symbols
        if param == 'x':
            return [sympy.Eq(x, value)]
        elif param == 'y':
            return [sympy.Eq(y, value)]
        else:
            raise IncorrectParamValue(f'Unexpected param {param}')


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
    all_parameters = ['x1', 'y1', 'x2', 'y2', 'length', 'angle']
    base_parameters = ['x1', 'y1', 'x2', 'y2']

    @contract(start='tuple(number, number) | None',
              angle='number | None', length='number, >0 | None')
    def __init__(self, start=(0, 0), angle=0, length=1):
        super().__init__(start, angle)
        self._i_length = float(length)

    @property
    def _length(self):
        return self._i_length

    @_length.setter
    @contract(value='number, >0')
    def _length(self, value):
        self._i_length = float(value)

    @classmethod
    @contract(x1='number', y1='number', x2='number', y2='number')
    def from_coordinates(cls, x1, y1, x2, y2):
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
        length = segment_length(x1, y1, x2, y2)
        angle = segment_angle(x1, y1, x2, y2)

        return cls(start=(x1, y1), angle=angle, length=length)

    @contract(returns='tuple(float, float, float, float)')
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

    @contract(returns='dict(str: float)')
    def get_params(self):
        """Return all parameters.

       Returns
       -------
       params: dict(str -> float)
           Keys are ['x1', 'y1', 'x2', 'y2', 'length', 'angle'].
       """
        return {
            'x1': self._base[0],
            'y1': self._base[1],
            'x2': self._base[0] + self._length * np.cos(self._angle),
            'y2': self._base[1] + self._length * np.sin(self._angle),
            'length': self._length,
            'angle': self._angle
        }

    @contract(param_name='str', value='number')
    def set_param(self, param_name, value):
        """Set parameter of figure.

        Parameters
        ----------
        param_name: str
            Name of parameter to set value.
            Must be in ['x1', 'y1', 'x2', 'y2', 'length', 'angle'].
        value: int or float
            Value too set.

        Returns
        -------
        self

        Raises
        ------
        IncorrectParamValue: if param is incorrect.
        """

        if param_name == 'x1':
            self._base = (float(value), self._base[1])
        elif param_name == 'y1':
            self._base = (self._base[0], float(value))
        elif param_name == 'length':
            self._length = float(value)
        elif param_name == 'angle':
            self._angle = float(value)
        elif param_name in ('x2', 'y2'):
            base_repr = list(self.get_base_representation())
            if param_name == 'x2':
                base_repr[2] = value
            else:
                base_repr[3] = value  # y2
            length = segment_length(*base_repr)
            angle = segment_angle(*base_repr)
            self._length, self._angle = length, angle
        else:
            raise IncorrectParamValue(
                f'Incorrect name of parameter: {param_name}.')

        return self

    @contract(symbols='list[4]', param='str', value='number', returns='list')
    def get_setter_equations(self, symbols: list, param: str, value: float):
        """Return equations for setting parameters of segment.

        Parameters
        ----------
        symbols: list[sympy.Symbol]
            Symbols for segment.
            Must contain 4 elements: symbols for x1, y1, x2, y2.
        param: str
            Name of parameter to set value.
            Must be in ['x1', 'y1', 'x2', 'y2', 'length', 'angle'].
        value: int or float
            Value to set.

        Returns
        -------
        equations: list[sympy.Eq]
            List of equations.

        Raises
        ------
            IncorrectParamValue: if param is incorrect.
        """
        x1, y1, x2, y2 = symbols
        if param == 'x1':
            return [sympy.Eq(x1, value)]
        elif param == 'y1':
            return [sympy.Eq(y1, value)]
        elif param == 'x2':
            return [sympy.Eq(x2, value)]
        elif param == 'y2':
            return [sympy.Eq(y2, value)]
        elif param == 'length':
            return [sympy.Eq((x2 - x1) ** 2 + (y2 - y1) ** 2, value ** 2)]
        elif param == 'angle':
            raise NotImplementedError
            # return [sympy.Eq(y1, value)]
            # TODO
        else:
            raise IncorrectParamValue(f'Unexpected param {param}')
