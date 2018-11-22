import pytest
from numpy import isclose, pi
import numpy.random as random
from contracts import ContractNotRespected

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
        with pytest.raises(ContractNotRespected):
            Figure(('1', 2), 1)
        with pytest.raises(ContractNotRespected):
            Figure((1, 2), '1')

    def test_representation(self):
        f = Figure()
        rep = f.get_base_representation()
        assert rep == NotImplemented

    def test_incorrect_moving(self):
        f = Figure()
        with pytest.raises(ContractNotRespected):
            f.move('1', 2)
        with pytest.raises(ContractNotRespected):
            f.move(1, '2')

    def test_incorrect_rotation(self):
        f = Figure()
        with pytest.raises(ContractNotRespected):
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

    def test_getting_params(self):
        p = Point((1, 2))
        res = p.get_params()
        assert isinstance(res, dict)
        assert set(res.keys()) == {'x', 'y'}
        assert res['x'] == 1.0 and res['y'] == 2.0

    def test_setting_param(self):
        p = Point((1, 2))

        p.set_param('x', 10)
        rep = p.get_base_representation()
        assert all(isclose(rep, (10, 2)))

        p.set_param('y', 20)
        rep = p.get_base_representation()
        assert all(isclose(rep, (10, 20)))

        with pytest.raises(IncorrectParamValue):
            p.set_param('y2', 100)


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
        with pytest.raises(ContractNotRespected):
            Segment(('1', 2), 1)
        with pytest.raises(ContractNotRespected):
            Segment((1, 2), '1')
        with pytest.raises(ContractNotRespected):
            Segment((1, 1), 1, '1')
        for i in [-1, 0]:
            with pytest.raises(ContractNotRespected):
                Segment((1, 2), 0, i)

    def test_create_from_point(self):
        for coo in random.random((10, 4)) * 100 - 50:
            s = Segment.from_coordinates(*coo)
            assert all(isclose(coo, s.get_base_representation()))

    def test_incorrect_create_from_point(self):
        for i in range(4):
            a = [1, 1, 1, 1]
            a[i] = '1'
            with pytest.raises(ContractNotRespected):
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

    def test_getting_params(self):
        s = Segment((1, 2), 0, 10)
        res = s.get_params()
        assert isinstance(res, dict)
        assert set(res.keys()) == {'x1', 'y1', 'x2', 'y2', 'length', 'angle'}
        assert res['x1'] == 1.0 \
            and res['y1'] == 2.0 \
            and res['x2'] == 11.0 \
            and res['y2'] == 2.0 \
            and res['length'] == 10.0 \
            and res['angle'] == 0.0

    def test_setting_param(self):
        s = Segment((1, 2), 0, 10)

        s.set_param('x1', 0)
        rep = s.get_base_representation()
        assert all(isclose(rep, (0, 2, 10, 2)))

        s.set_param('y1', 0)
        rep = s.get_base_representation()
        assert all(isclose(rep, (0, 0, 10, 0)))

        s.set_param('y2', 5)
        rep = s.get_base_representation()
        assert all(isclose(rep, (0, 0, 10, 5)))

        s.set_param('x2', 0)
        rep = s.get_base_representation()
        assert all(isclose(rep, (0, 0, 0, 5)))

        s.set_param('length', 7)
        rep = s.get_base_representation()
        assert all(isclose(rep, (0, 0, 0, 7)))

        s.set_param('angle', 0)
        rep = s.get_base_representation()
        assert all(isclose(rep, (0, 0, 7, 0)))

        with pytest.raises(IncorrectParamValue):
            s.set_param('y', 100)
