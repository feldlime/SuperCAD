from numpy import isclose
from bindings import *
from figures import Point, Segment
import numpy as np


def is_sequences_equal(s1, s2, use: str = 'equal', sort=True):
    """use can be {'equal', 'is', 'equal_types'}"""
    if type(s1) != type(s2):
        return False
    if len(s1) != len(s2):
        return False

    def equal(e1, e2):
        if use == 'equal':
            return e1 == e2
        elif use == 'is':
            return e1 == e2
        elif use == 'equal_types':
            return type(e1) == type(e2)

    if sort:
        s1 = sorted(s1)
        s2 = sorted(s2)
    for elem1, elem2 in zip(s1, s2):
        if not equal(elem1, elem2):
            return False
    return True


class TestBindings:
    def test_bindings_and_bindings_creation(self):
        figures = {
            'point1': Point((1, 1)),
            'point2': Point((2, 3)),
            'segment1': Segment((0, 0), 0, 7),
            'segment2': Segment.from_coordinates(3, 8, 7, 4),
            'segment3': Segment((5, 5), np.pi / 2, 5),
        }

        bindings = create_bindings(
            figures, circle_bindings_radius=0.5, segment_bindings_margin=0.2
        )

        correct_bindings_types = (
            [PointBinding] * 2
            + ([SegmentSpotBinding] * 3 + [FullSegmentBinding]) * 3
            + [SegmentsIntersectionBinding] * 3
        )

        assert is_sequences_equal(
            list(map(type, bindings)), correct_bindings_types, sort=False
        )

        def get_binding(figure_names, binding_type, spot_type=None):
            for binding in bindings:
                objects_names = binding.get_object_names()
                if is_sequences_equal(
                    figure_names, objects_names
                ) and isinstance(binding, binding_type):
                    if (
                        binding_type != SegmentSpotBinding
                        or binding.spot_type == spot_type
                    ):
                        return binding

        # Point1
        point1_b = get_binding(['point1'], PointBinding)
        assert point1_b.check(10, 10) is None
        assert isclose(point1_b.check(1.2, 1.2), 0.2 * 2 ** 0.5)
        assert all(isclose(point1_b.bind(), (1, 1)))

        figures['point1'].move(dy=2)
        assert point1_b.check(1.4, 3.4) is None
        assert all(isclose(point1_b.bind(), (1, 3)))

        # Segment1
        segment1_center_b = get_binding(
            ['segment1'], SegmentSpotBinding, 'center'
        )
        assert isclose(segment1_center_b.check(3.5, 0.1), 0.1)
        assert all(isclose(segment1_center_b.bind(), (3.5, 0)))

        segment1_full_b = get_binding(['segment1'], FullSegmentBinding)
        assert isclose(segment1_full_b.check(3, 0.15), 0.15)
        assert isclose(segment1_full_b.check(7.15, 0), 0.15)
        assert segment1_full_b.check(7.15, 0.15) is None
        assert all(isclose(segment1_full_b.bind(2.3, -0.7), (2.3, 0)))

        # Intersections
        s1_s2_b = get_binding(
            ['segment1', 'segment2'], SegmentsIntersectionBinding
        )
        assert all(isclose(s1_s2_b.bind(), (11, 0)))

        s1_s3_b = get_binding(
            ['segment1', 'segment3'], SegmentsIntersectionBinding
        )
        assert all(isclose(s1_s3_b.bind(), (5, 0)))

        s2_s3_b = get_binding(
            ['segment2', 'segment3'], SegmentsIntersectionBinding
        )
        assert all(isclose(s2_s3_b.bind(), (5, 6)))

    def test_choosing_best_bindings(self):
        figures = {
            'point1': Point((1, 1)),
            'point2': Point((2, 3)),
            'segment1': Segment((0, 0), 0, 7),
            'segment2': Segment.from_coordinates(3, 8, 7, 4),
            'segment3': Segment((5, 5), np.pi / 2, 5),
        }

        bindings = create_bindings(
            figures, circle_bindings_radius=0.5, segment_bindings_margin=0.2
        )

        def get_binding(figure_names, binding_type, spot_type=None):
            for binding in bindings:
                objects_names = binding.get_object_names()
                if is_sequences_equal(
                    figure_names, objects_names
                ) and isinstance(binding, binding_type):
                    if (
                        binding_type != SegmentSpotBinding
                        or binding.spot_type == spot_type
                    ):
                        return binding

        figures['point2'].set_param('x', 3).set_param('y', 8)

        # No bindings
        bb = choose_best_bindings(bindings, 10, 10)
        assert is_sequences_equal(bb, [])

        # Just point
        bb = choose_best_bindings(bindings, 1.1, 1.1)
        point1_b = get_binding(['point1'], PointBinding)
        assert is_sequences_equal(bb, [point1_b], use='is')

        # Full segment
        bb = choose_best_bindings(bindings, 3, 0.15)
        segment1_full_b = get_binding(['segment1'], FullSegmentBinding)
        assert is_sequences_equal(bb, [segment1_full_b], use='is')

        # Segment center beat full segment
        bb = choose_best_bindings(bindings, 3.5, 0.15)
        segment1_center_b = get_binding(
            ['segment1'], SegmentSpotBinding, 'center'
        )
        # No full binding!
        assert is_sequences_equal(bb, [segment1_center_b], use='is')

        # To points with same coordinates
        bb = choose_best_bindings(bindings, 2.9, 7.9)
        s2_start_b = get_binding(['segment2'], SegmentSpotBinding, 'start')
        point2_b = get_binding(['point2'], PointBinding)
        answer_v1 = [s2_start_b, point2_b]
        answer_v2 = [point2_b, s2_start_b]
        assert is_sequences_equal(
            bb, answer_v1, use='is', sort=False
        ) or is_sequences_equal(bb, answer_v2, use='is', sort=False)
