import pytest
import numpy as np
import numpy.random as random

from project import CADProject
from figures import Point, Segment
from restrictions import *
from
from utils import (
    IncorrectParamType,
    IncorrectParamValue,
    IncorrectParamError
)


def assert_flat_dicts_equal(d1, d2, is_close=False):
    assert isinstance(d1, dict)
    assert isinstance(d2, dict)
    assert set(d1.keys()) == set(d2.keys())
    for k, v1 in d1.items():
        v2 = d2[k]
        if is_close:
            assert np.isclose(v1, v2)
        else:
            assert v1 == v2


def assert_2_level_dicts_equal(d1, d2, is_close=False):
    assert isinstance(d1, dict)
    assert isinstance(d2, dict)
    assert set(d1.keys()) == set(d2.keys())
    for k, v1 in d1.items():
        v2 = d2[k]
        assert_flat_dicts_equal(v1, v2, is_close)


def assert_sequences_equal(s1, s2):
    assert type(s1) == type(s2)
    assert len(s1) == len(s2)
    for e1, e2 in zip(sorted(s1), sorted(s2)):
        assert e1 == e2


class TestProject():
    def test_full_pass(self):
        project = CADProject()

        # Add figures
        point1 = Point((1, 2))
        point1_name = project.add_figure(point1)
        point2 = Point((5, 6))
        point2_name = project.add_figure(point2)
        segment1 = Segment((0, 0), 10, 0)
        segment1_name = project.add_figure(segment1)
        segment2 = Segment((0, 0), 5, 1.5)
        segment2_name = project.add_figure(segment2)

        # Change parameter
        project.change_figure(point1_name, 'y', 2)
        project.change_figure(segment1_name, 'length', 7)
        # project.change_figure(segment2_name, 'angle', np.pi/2)

        # Check
        figur
        # Try move
        # project.move_figure()




