"""Module with classes of geometry restrictions."""
import sympy
from sympy import symbols, Eq


def get_full_symbol_name(object_name, symbol_name):
    return f'{object_name}__{symbol_name}'


class Restriction:
    def get_equations(self, **kwargs) -> list:
        raise NotImplementedError

    @staticmethod
    def _get_symbols(name, symbols_names):
        string = ' '.join([get_full_symbol_name(name, sym)
                           for sym in symbols_names])
        return symbols(string)


class FixedPoint(Restriction):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def get_equations(self, point_name):
        x, y = self._get_symbols(point_name, ['x', 'y'])
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
