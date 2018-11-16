import pytest
from numpy import isclose, pi
import numpy.random as random

from figures import Figure, Point, Segment
from utils import (
    IncorrectParamType,
    IncorrectParamValue,
    IncorrectParamError
)


# noinspection PyTypeChecker
class TestFigure:
    def test_normal_creation(self):
        f = Figure((1, 2), 1)
        assert isinstance(f, Figure)
        f = Figure((1., 2.), 1)
        assert isinstance(f, Figure)
        f = Figure((1, 2), 1.)
        assert isinstance(f, Figure)
        f = Figure()
        assert isinstance(f, Figure)

    def test_incorrect_creation(self):
        with pytest.raises(IncorrectParamValue):
            Figure(('1', 2), 1)
        with pytest.raises(IncorrectParamType):
            Figure((1, 2), '1')

    def test_representation(self):
        f = Figure()
        rep = f.get_base_representation()
        assert rep == NotImplemented

    def test_incorrect_moving(self):
        f = Figure()
        with pytest.raises(IncorrectParamType):
            f.move('1', 2)
        with pytest.raises(IncorrectParamType):
            f.move(1, '2')

    def test_incorrect_rotation(self):
        f = Figure()
        with pytest.raises(IncorrectParamType):
            f.rotate('2')


# noinspection PyArgumentList
class TestPoint:
    def test_normal_creation(self):
        p = Point((1, 2))
        rep = p.get_base_representation()
        assert all(isclose(rep, (1, 2)))

    def test_incorrect_creation(self):
        with pytest.raises(TypeError):
            Point((1, 2), 1)

    def test_moving(self):
        p = Point((1, 2))
        p.move(3, 4)
        rep = p.get_base_representation()
        assert all(isclose(rep, (4, 6)))

    def test_not_rotation(self):
        p = Point((1, 2))
        res = p.rotate(1.5)
        rep = p.get_base_representation()
        assert all(isclose(rep, (1, 2))) and res == NotImplemented

    def test_creation_from_coordinates(self):
        p = Point.from_coordinates(0, 10)
        rep = p.get_base_representation()
        assert all(isclose(rep, (0, 10)))

    def test_incorrect_creation_from_coordinates(self):
        with pytest.raises(TypeError):
            Point.from_coordinates(y=10)


# noinspection PyTypeChecker
class TestSegment:
    def test_default_creation(self):
        s = Segment()
        rep = s.get_base_representation()
        assert rep == (0.0, 0.0, 1.0, 0.0)

    def test_normal_creation(self):
        s = Segment((1, 2), 0, 3)
        rep = s.get_base_representation()
        assert all(isclose((1, 2, 4, 2), rep))

        s = Segment((1, 2), pi / 2, 3)
        rep = s.get_base_representation()
        assert all(isclose((1, 2, 1, 5), rep))

    def test_incorrect_creation(self):
        with pytest.raises(IncorrectParamValue):
            Segment(('1', 2), 1)
        with pytest.raises(IncorrectParamType):
            Segment((1, 2), '1')
        with pytest.raises(IncorrectParamType):
            Segment((1, 1), 1, '1')
        for i in range(-1, 1):
            with pytest.raises(IncorrectParamValue):
                Segment((1, 2), 0, i)

    def test_create_from_point(self):
        for coo in random.random((10, 4)) * 100 - 50:
            s = Segment.from_coordinates(*coo)
            assert all(isclose(coo, s.get_base_representation()))

    def test_incorrect_create_from_point(self):
        for i in range(4):
            a = [1, 1, 1, 1]
            a[i] = '1'
            with pytest.raises(IncorrectParamError):
                Segment.from_coordinates(*a)

    def test_move(self):
        for coo in random.random((10, 4)) * 100 - 50:
            s = Segment((coo[2], coo[3]), 0, 1)
            s.move(coo[0], coo[1])
            assert all(isclose(
                (coo[0]+coo[2], coo[1]+coo[3], coo[0]+coo[2]+1, coo[1]+coo[3]),
                s.get_base_representation()))

    def test_rotate(self):
        s = Segment((1, 1), 0, 1)
        s.rotate(pi)
        assert all(isclose((1, 1, 0, 1), s.get_base_representation()))
        s.rotate(pi/2)
        assert all(isclose((1, 1, 1, 0), s.get_base_representation()))
        s.rotate(-pi)
        assert all(isclose((1, 1, 1, 2), s.get_base_representation()))
        s.rotate(-pi/2)
        assert all(isclose((1, 1, 2, 1), s.get_base_representation()))
