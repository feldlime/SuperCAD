"""Module with classes of geometry restrictions."""

from sympy import Symbol, Eq


class Restriction:
    def get_equations(self, **kwargs) -> list:
        raise NotImplementedError


class FixedPoint(Restriction):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def get_equations(self, point_symbols: dict):
        x, y = point_symbols['x'], point_symbols['y']
        equations = [
            Eq(x, self._x),
            Eq(y, self._y)
        ]
        return equations


class FixedLength(Restriction):
    def __init__(self, length):
        """

        length:
            If None use current length.
        """
        self._length = length

    def get_equations(self, name_segment):
        pass


# more
