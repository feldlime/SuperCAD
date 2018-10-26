import pytest
from numpy import isclose
from utils import *


def test_magnitude():
    res = magnitude(1, 1, 4, 5)
    answer = 5
    assert isclose(res, answer)

    res = magnitude(1, 1, 4, -3)
    answer = 5
    assert isclose(res, answer)

    res = magnitude(1, 1, 1, 1)
    answer = 0
    assert isclose(res, answer)


def test_coordinates():
    coo = Coordinates((1, 2))
    res = coo.get()
    answer = (1, 2)
    assert all(isclose(res, answer))

    a = 5
    fun = lambda: (a, 3)
    coo = Coordinates(fun)
    res = coo.get()
    answer = (5, 3)
    assert all(isclose(res, answer))

    a = 10
    res = coo.get()
    answer = (10, 3)
    assert all(isclose(res, answer))

    with pytest.raises(IncorrectParamType):
        Coordinates([1, 2])

    with pytest.raises(IncorrectParamError):
        Coordinates((1, 2, 3))

    with pytest.raises(IncorrectParamError):
        Coordinates((1, '2'))
