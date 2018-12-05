from restrictions import (
    PointFixed,
    SegmentLengthFixed,
    SegmentSpotFixed,
    PointAndSegmentSpotJoint
)
from project import CADProject, ActionImpossible
from figures import Point, Segment
from bindings import choose_best_bindings
import pytest
import numpy as np
from utils import (
    IncorrectParamValue,
)
import os


def is_equal(v1, v2, equal_type='equal'):
    if equal_type == 'equal':
        return v1 == v2
    elif equal_type == 'close':
        return np.isclose(v1, v2)
    elif equal_type == 'type':
        return type(v1) == type(v2)
    else:
        raise ValueError(f'Unknown equal_type {equal_type}')


def is_flat_dicts_equal(d1, d2, equal_type='equal'):
    if not isinstance(d1, dict):
        return False
    if not isinstance(d2, dict):
        return False
    if set(d1.keys()) != set(d2.keys()):
        return False
    for k, v1 in d1.items():
        v2 = d2[k]
        if not is_equal(v1, v2, equal_type):
            return False
    return True


def is_2_level_dicts_equal(d1, d2, equal_type='equal'):
    if not isinstance(d1, dict):
        return False
    if not isinstance(d2, dict):
        return False
    if set(d1.keys()) != set(d2.keys()):
        return False
    for k, v1 in d1.items():
        v2 = d2[k]
        if not is_flat_dicts_equal(v1, v2, equal_type):
            return False
    return True


def is_sequences_equal(s1, s2, equal_type='equal'):
    if type(s1) != type(s2):
        return False
    if len(s1) != len(s2):
        return False
    for e1, e2 in zip(sorted(s1), sorted(s2)):
        if not is_equal(e1, e2, equal_type):
            return False
    return True


def check_objects_types(objects, correct_types_dict):
    if set(objects.keys()) != set(correct_types_dict.keys()):
        return False
    for k, v in objects.items():
        if not is_equal(type(v), correct_types_dict[k]):
            return False
    return True


class TestProject:
    @staticmethod
    def _is_figures_correct(figures, correct_values):
        if set(figures.keys()) != set(correct_values.keys()):
            return False
        for name, f in figures.items():
            if not is_sequences_equal(
                f.get_base_representation(),
                correct_values[name],
                equal_type='close'
            ):
                return False
        return True

    def test_addition_and_deletion_figures(self):
        project = CADProject()

        # Add figures
        point1 = Point((1, 2))
        point1_name = project.add_figure(point1)
        correct_types = {
            point1_name: Point,
        }
        assert check_objects_types(project.figures, correct_types)

        point2 = Point((5, 6))
        point2_name = project.add_figure(point2)
        correct_types = {
            point1_name: Point,
            point2_name: Point,
        }
        assert check_objects_types(project.figures, correct_types)

        segment1 = Segment((0, 0), 0, 10)
        segment1_name = project.add_figure(segment1)
        correct_types = {
            point1_name: Point,
            point2_name: Point,
            segment1_name: Segment
        }
        assert check_objects_types(project.figures, correct_types)

        # Remove figures
        project.remove_figure(point2_name)
        correct_types = {
            point1_name: Point,
            segment1_name: Segment
        }
        assert check_objects_types(project.figures, correct_types)

        with pytest.raises(IncorrectParamValue):
            project.remove_figure(point2_name)

        project.remove_figure(segment1_name)
        correct_types = {
            point1_name: Point,
        }
        assert check_objects_types(project.figures, correct_types)

        project.remove_figure(point1_name)
        correct_types = {
        }
        assert check_objects_types(project.figures, correct_types)

    def test_changing_parameters(self):
        project = CADProject()

        # Add figures
        point1 = Point((1, 1))
        point1_name = project.add_figure(point1)
        point2 = Point((5, 6))
        point2_name = project.add_figure(point2)
        segment1 = Segment((0, 0), 0, 10)
        segment1_name = project.add_figure(segment1)

        project.change_figure(point1_name, 'y', 2)
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (0, 0, 10, 0)
        }
        assert self._is_figures_correct(project.figures, correct_figures)

        new_len = 7
        project.change_figure(segment1_name, 'length', new_len)
        answer_1 = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: ((10-new_len) / 2, 0, 10 - (10-new_len) / 2, 0)
        }
        answer_2 = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (0, 0, new_len, 0)
        }
        answer_3 = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (10 - new_len, 0, 10, 0)
        }
        assert self._is_figures_correct(project.figures, answer_1) \
            or self._is_figures_correct(project.figures, answer_2) \
            or self._is_figures_correct(project.figures, answer_3)

    def test_moving(self):
        project = CADProject()

        # Add figures
        point1 = Point((1, 1))
        point1_name = project.add_figure(point1)
        point2 = Point((5, 6))
        point2_name = project.add_figure(point2)
        segment1 = Segment((0, 0), 0, 10)
        segment1_name = project.add_figure(segment1)

        # Move point to (3, 4)
        bb = choose_best_bindings(project.bindings, 1.1, 1)[0]
        project.move_figure(bb, 3, 4)
        correct_figures = {
            point1_name: (3, 4),
            point2_name: (5, 6),
            segment1_name: (0, 0, 10, 0)
        }
        assert self._is_figures_correct(project.figures, correct_figures)
        project.commit()

        # Move segment end to (7, 7)
        bb = choose_best_bindings(project.bindings, 10, 0)[0]
        project.move_figure(bb, 7, 7)
        correct_figures = {
            point1_name: (3, 4),
            point2_name: (5, 6),
            segment1_name: (0, 0, 7, 7)
        }
        assert self._is_figures_correct(project.figures, correct_figures)
        project.commit()

    def test_addition_and_deletion_restrictions(self):
        project = CADProject()

        # Add figures
        point1 = Point((1, 2))
        point1_name = project.add_figure(point1)
        point2 = Point((5, 6))
        point2_name = project.add_figure(point2)
        segment1 = Segment((0, 0), 0, 10)
        segment1_name = project.add_figure(segment1)

        # Fix point1
        r = PointFixed(1, 2)
        p1_fixed_name = project.add_restriction(r, (point1_name,))
        correct_types = {
            p1_fixed_name: PointFixed,
        }
        assert check_objects_types(project.restrictions, correct_types)
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (0, 0, 10, 0)
        }
        assert self._is_figures_correct(project.figures, correct_figures)

        # Join point1 and start of segment1
        r = PointAndSegmentSpotJoint(spot_type='start')
        p1_s1s_joint_name = project.add_restriction(
            r, (point1_name, segment1_name))
        correct_types = {
            p1_fixed_name: PointFixed,
            p1_s1s_joint_name: PointAndSegmentSpotJoint
        }
        assert check_objects_types(project.restrictions, correct_types)
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (1, 2, 10, 0)  # Segment set. save length and angle
        }
        assert self._is_figures_correct(project.figures, correct_figures)

        # Fix end of segment1
        r = SegmentSpotFixed(1, 7, spot_type='end')
        s1e_fixed_name = project.add_restriction(r, (segment1_name,))
        correct_types = {
            p1_fixed_name: PointFixed,
            p1_s1s_joint_name: PointAndSegmentSpotJoint,
            s1e_fixed_name: SegmentSpotFixed
        }
        assert check_objects_types(project.restrictions, correct_types)
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (1, 2, 1, 7)
        }
        assert self._is_figures_correct(project.figures, correct_figures)

        # Remove fix end of segment1
        project.remove_restriction(s1e_fixed_name)
        correct_types = {
            p1_fixed_name: PointFixed,
            p1_s1s_joint_name: PointAndSegmentSpotJoint
        }
        assert check_objects_types(project.restrictions, correct_types)
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (1, 2, 1, 7)
        }
        assert self._is_figures_correct(project.figures, correct_figures)

        # Fix length of segment1
        r = SegmentLengthFixed(3)
        s1_fixed_length_name = project.add_restriction(r, (segment1_name,))
        correct_types = {
            p1_fixed_name: PointFixed,
            p1_s1s_joint_name: PointAndSegmentSpotJoint,
            s1_fixed_length_name: SegmentLengthFixed
        }
        assert check_objects_types(project.restrictions, correct_types)
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (1, 2, 1, 5)
        }
        assert self._is_figures_correct(project.figures, correct_figures)

    def test_complex(self):
        project = CADProject()

        # Add figures
        point1 = Point((1, 2))
        point1_name = project.add_figure(point1)
        point2 = Point((5, 6))
        point2_name = project.add_figure(point2)
        segment1 = Segment((0, 0), 0, 10)
        segment1_name = project.add_figure(segment1)

        # Fix point1
        r = PointFixed(1, 2)
        _ = project.add_restriction(r, (point1_name,))
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (0, 0, 10, 0)
        }
        assert self._is_figures_correct(project.figures, correct_figures)

        # Join point1 and start of segment1
        r = PointAndSegmentSpotJoint(spot_type='start')
        _ = project.add_restriction(
            r, (point1_name, segment1_name))
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (1, 2, 10, 0)
        }
        assert self._is_figures_correct(project.figures, correct_figures)

        # Move segment end
        bb = choose_best_bindings(project.bindings, 10, 0)[0]
        project.move_figure(bb, 12, 2)
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (1, 2, 12, 2)  # Segment set. save length and angle
        }
        assert self._is_figures_correct(project.figures, correct_figures)
        project.commit()

        # Change length
        project.change_figure(segment1_name, 'length', 11)
        correct_figures = {
            point1_name: (1, 2),
            point2_name: (5, 6),
            segment1_name: (1, 2, 12, 2)
        }
        assert self._is_figures_correct(project.figures, correct_figures)

    def test_undo_redo_commit_rollback(self):
        project = CADProject()

        with pytest.raises(ActionImpossible):
            project.undo()

        # Add figures
        point1 = Point((1, 2))
        _ = project.add_figure(point1)
        point2 = Point((5, 6))
        point2_name = project.add_figure(point2)

        # Undo, redo, _commit inside
        with pytest.raises(ActionImpossible):
            project.redo()

        project.undo()
        assert point2_name not in project.figures
        project.redo()
        assert point2_name in project.figures

        project.undo()
        assert point2_name not in project.figures
        segment1 = Segment((0, 0), 0, 10)
        segment1_name = project.add_figure(segment1)
        with pytest.raises(ActionImpossible):
            project.redo()

        project.undo()
        assert segment1_name not in project.figures
        project.undo()
        assert not project.figures
        assert not project.bindings
        with pytest.raises(ActionImpossible):
            project.undo()

        # Commit & rollback
        point3 = Point((1, 1))
        point3_name = project.add_figure(point3)
        bb = choose_best_bindings(project.bindings, 1, 1)[0]
        project.move_figure(bb, 5, 5)
        assert project.figures[point3_name].get_params()['x'] == 5
        project.commit()
        assert project.figures[point3_name].get_params()['x'] == 5

        bb = choose_best_bindings(project.bindings, 5, 5)[0]
        project.move_figure(bb, 7, 7)
        assert project.figures[point3_name].get_params()['x'] == 7
        project.rollback()
        assert project.figures[point3_name].get_params()['x'] == 5
        project.rollback()
        assert project.figures[point3_name].get_params()['x'] == 5

    def test_save_and_load(self):
        project1 = CADProject()

        # Add figures
        point1 = Point((1, 2))
        point1_name = project1.add_figure(point1, 'p1')
        assert point1_name in project1.figures

        # Save
        filename = 'test_save_and_load.scad'
        project1.save(filename)

        # Load 1
        project2 = CADProject()
        project2.load(filename)
        assert point1_name in project2.figures

        # One more project
        project3 = CADProject()
        point2 = Point((0, 0))
        point2_name = project3.add_figure(point2, 'p2')
        assert point2_name in project3.figures
        assert point1_name not in project3.figures

        project3.load(filename)
        assert point2_name not in project3.figures
        assert point1_name in project3.figures

        os.remove(filename)

