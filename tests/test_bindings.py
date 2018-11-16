import pytest
import numpy as np
from numpy import isclose
from bindings import *
from figures import Point, Segment

from utils import (
    IncorrectParamType,
    IncorrectParamValue,
    IncorrectParamError
)


def is_sequences_equal(s1, s2):
    if type(s1) != type(s2):
        return False
    if len(s1) != len(s2):
        return False
    for e1, e2 in zip(sorted(s1), sorted(s2)):
        if e1 == e2:
            return False
    return True


class TestBindings:
    def test_bindings_and_bindings_creation(self):
        figures = {
            'point1': Point((1, 1)),
            'point2': Point((2, 3)),
            'segment1': Segment((0, 0), 0, 7),
            'segment2': Segment.from_coordinates(3, 8, 7, 4),
            'segment3': Segment((5, 5), np.pi / 2, 5)
        }

        bindings = create_bindings(
            figures,
            circle_bindings_radius=0.5,
            segment_bindings_margin=0.2
        )

        assert len(bindings) == 2 * 1 + 3 * 3 + 3

        def get_binding(figure_names, binding_type):
            for binding in bindings:
                objects_names = binding.get_object_names()
                if is_sequences_equal(figure_names, objects_names) \
                        and isinstance(binding, binding_type):
                    return binding

        # Point1
        point1_b = get_binding(['point1'], PointBinding)
        assert point1_b.check(10, 10) is None
        assert all(isclose(point1_b.check(1.2, 1.2), 0.2 * 2**0.5))
        assert all(isclose(point1_b.bind(), (1, 1)))

        figures['point1'].move(dy=2)
        assert point1_b.check(1.4, 3.4) is None
        assert all(isclose(point1_b.bind(), (1, 3)))

        # Segment1
        segment1_center_b = get_binding(['segment1'], SegmentCenterBinding)
        assert all(isclose(segment1_center_b.check(3.5, 0.1), 0.1))
        assert all(isclose(segment1_center_b.bind(), (3.5, 0)))

        segment1_full_b = get_binding(['segment1'], FullSegmentBinding)
        assert all(isclose(segment1_full_b.check(3, 0.15), 0.15))
        assert all(isclose(segment1_full_b.check(7.15, 0), 0.15))
        assert segment1_full_b.check(7.15, 0.15) is None
        assert all(isclose(segment1_center_b.bind(2.3, -0.7), (2.3, 0)))

        # Intersections
        s1_s2_b = get_binding(
            ['segment1', 'segment2'], SegmentsIntersectionBinding)
        assert all(isclose(s1_s2_b.bind(), (11, 0)))

        s1_s3_b = get_binding(
            ['segment1', 'segment3'], SegmentsIntersectionBinding)
        assert all(isclose(s1_s3_b.bind(), (5, 0)))

        s2_s3_b = get_binding(
            ['segment2', 'segment3'], SegmentsIntersectionBinding)
        assert all(isclose(s2_s3_b.bind(), (5, 6)))

