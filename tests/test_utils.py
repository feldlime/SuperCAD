import pytest

from utils import *
import numpy as np


def test_segment_length():
    res = segment_length(1, 1, 4, 5)
    answer = 5
    assert np.isclose(res, answer)

    res = segment_length(1, 1, 4, -3)
    answer = 5
    assert np.isclose(res, answer)

    res = segment_length(1, 1, 1, 1)
    answer = 0
    assert np.isclose(res, answer)


def test_simplify_angle():
    res = simplify_angle(1.2)
    assert np.isclose(res, 1.2)

    res = simplify_angle(0)
    assert np.isclose(res, 0)

    res = simplify_angle(-1.2)
    assert np.isclose(res, 2 * np.pi - 1.2)


def test_segment_angle():
    res = segment_angle(1, 1, 5, 5)
    assert np.isclose(res, np.pi / 4)

    res = segment_angle(1, 1, -4, 6)
    assert np.isclose(res, 3 * np.pi / 4)

    res = segment_angle(1, 1, -5, -5)
    assert np.isclose(res, 5 * np.pi / 4)

    res = segment_angle(1, 1, 6, -4)
    assert np.isclose(res, 7 * np.pi / 4)

    res = segment_angle(1, 1, 5, 1)
    assert np.isclose(res, 0)

    res = segment_angle(1, 1, -5, 1)
    assert np.isclose(res, np.pi)

    res = segment_angle(1, 1, 1, 5)
    assert np.isclose(res, np.pi / 2)

    res = segment_angle(1, 1, 1, -4)
    assert np.isclose(res, 3 * np.pi / 2)

    res = segment_angle(1, 1, 1, 1)
    assert np.isclose(res, 0)


def test_stack():
    s = Stack()

    s.push(1)
    assert s.get_head() == 1

    s.push(2)
    assert s.get_head() == 2

    assert s.get_head() == 2
    assert s.get_head() == 2

    assert s.pop() == 2
    assert s.get_head() == 1

    assert s.pop() == 1
    with pytest.raises(EmptyStackError):
        s.get_head()

    with pytest.raises(EmptyStackError):
        s.pop()

    s.push(3)
    assert s.get_head() == 3

    s.clear()
    with pytest.raises(EmptyStackError):
        s.pop()
    with pytest.raises(EmptyStackError):
        s.get_head()
