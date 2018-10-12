import pytest
from numpy import isclose
from figures import *


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
        with pytest.raises(IncorrectParamType):
            f = Figure(('1', 2), 1)
            f = Figure((1, 2), '1')

    def test_representation(self):
        f = Figure()
        rep = f.get_base_representation()
        assert rep == NotImplemented

    def test_incorrect_moving(self):
        f = Figure()
        with pytest.raises(IncorrectParamType):
            f.move('1', 2)
            f.move(1, '2')

    def test_incorrect_rotation(self):
        f = Figure()
        with pytest.raises(IncorrectParamType):
            f.rotate('2')


class TestPoint:
    def test_normal_creation(self):
        p = Point((1, 2))
        rep = p.get_base_representation()
        assert all(isclose(rep, (1, 2)))

    def test_incorrect_creation(self):
        with pytest.raises(TypeError):
            p = Point((1, 2), 1)

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
            p = Point.from_coordinates(y=10)


class TestSegment:
    def test_default_creation(self):
        s = Segment()
        rep = s.get_base_representation()
        assert rep == (0.0, 0.0, 1.0, 0.0)

    def test_normal_creation(self):
        s = Segment((1, 2), 0, 3)
        rep = s.get_base_representation()
        assert all(isclose((1, 2, 4, 2), rep))

        s = Segment((1, 2), np.pi / 2, 3)
        rep = s.get_base_representation()
        assert all(isclose((1, 2, 1, 5), rep))

    def test_incorrect_creation(self):
        with pytest.raises(IncorrectParamType):
            s = Segment(('1', 2), 1)
            s = Segment((1, 2), '1')

    @pytest.mark.randomize(length=int, min_num=-100, max_num=100, ncalls=10)
    def test_create_from_point(self, length):
        s = Segment.from_points(0, 0, length, 0)
        assert all(isclose((0, 0, length, 0), s.get_base_representation()))



