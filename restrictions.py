"""Module with classes of geometry restrictions."""

from utils import ReferencedToObjects
from figures import Point, Segment

from numpy import pi
from sympy import Eq
from contracts import contract


class Restriction:
    _object_types = []

    def __init__(self):
        pass

    @property
    def _n_objects(self):
        return len(self._object_types)

    def get_equations(self, **kwargs) -> list:
        raise NotImplementedError


# Point

class PointFixed(Restriction, ReferencedToObjects):
    _object_types = [Point]

    @contract(x='number', y='number')
    def __init__(self, x, y):
        super().__init__()
        self._x = x
        self._y = y

    @contract(symbols='dict')
    def get_equations(self, symbols: dict):
        x, y = symbols['x'], symbols['y']
        equations = [
            Eq(x, self._x),
            Eq(y, self._y)
        ]
        return equations


# Two points

class PointsJoint(Restriction, ReferencedToObjects):
    _object_types = [Point, Point]

    @contract(symbols_point_1='dict', symbols_point_2='dict')
    def get_equations(self, symbols_point_1: dict, symbols_point_2: dict):
        x1, y1 = symbols_point_1['x'], symbols_point_1['y']
        x2, y2 = symbols_point_2['x'], symbols_point_2['y']
        equations = [
            Eq(x1, x2),
            Eq(y1, y2)
        ]
        return equations


# Segment

class SegmentFixed(Restriction, ReferencedToObjects):
    _object_types = [Segment]

    @contract(x1='number', y1='number', x2='number', y2='number')
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

    @contract(symbols='dict')
    def get_equations(self, symbols: dict):
        x1, y1 = symbols['x1'], symbols['y1']
        x2, y2 = symbols['x2'], symbols['y2']
        equations = [
            Eq(x1, self._x1),
            Eq(y1, self._y1),
            Eq(x2, self._x2),
            Eq(y2, self._y2)
        ]
        return equations


class SegmentStartFixed(Restriction, ReferencedToObjects):
    _object_types = [Segment]

    @contract(x='number', y='number')
    def __init__(self, x, y):
        super().__init__()
        self._x = x
        self._y = y

    @contract(symbols='dict')
    def get_equations(self, symbols: dict):
        x1, y1 = symbols['x1'], symbols['y1']
        equations = [
            Eq(x1, self._x),
            Eq(y1, self._y),
        ]
        return equations


class SegmentEndFixed(Restriction, ReferencedToObjects):
    _object_types = [Segment]

    @contract(x='number', y='number')
    def __init__(self, x, y):
        super().__init__()
        self._x = x
        self._y = y

    @contract(symbols='dict')
    def get_equations(self, symbols: dict):
        x2, y2 = symbols['x2'], symbols['y2']
        equations = [
            Eq(x2, self._x),
            Eq(y2, self._y),
        ]
        return equations


class SegmentCenterFixed(Restriction, ReferencedToObjects):
    _object_types = [Segment]

    @contract(x='number', y='number')
    def __init__(self, x, y):
        super().__init__()
        self._x = x
        self._y = y

    @contract(symbols='dict')
    def get_equations(self, symbols: dict):
        x1, y1 = symbols['x1'], symbols['y1']
        x2, y2 = symbols['x2'], symbols['y2']
        # TODO
        pass


class SegmentLengthFixed(Restriction, ReferencedToObjects):
    _object_types = [Segment]

    @contract(length='number,>0')
    def __init__(self, length):
        super().__init__()
        self._length = length

    @contract(symbols='dict')
    def get_equations(self, symbols: dict):
        # TODO
        pass


class SegmentAngleFixed(Restriction, ReferencedToObjects):
    _object_types = [Segment]

    @contract(angle='number, > 0, < 2 * $pi')
    def __init__(self, angle):
        super().__init__()
        self._angle = angle

    @contract(symbols='dict')
    def get_equations(self, symbols: dict):
        # TODO
        pass


class SegmentsHorizontal(Restriction, ReferencedToObjects):
    _object_types = [Segment]

    @contract(symbols='dict')
    def get_equations(self, symbols: dict):
        # TODO
        pass


class SegmentsVertical(Restriction, ReferencedToObjects):
    _object_types = [Segment]

    @contract(symbols='dict')
    def get_equations(self, symbols: dict):
        # TODO
        pass


# Segments

class SegmentsAngleBetweenFixed(Restriction, ReferencedToObjects):
    _object_types = [Segment, Segment]

    @contract(symbols_segment_1='dict', symbols_segment_2='dict')
    def get_equations(self, symbols_segment_1: dict, symbols_segment_2: dict):
        # TODO
        pass


class SegmentsParallel(Restriction, ReferencedToObjects):
    _object_types = [Segment, Segment]

    @contract(symbols_segment_1='dict', symbols_segment_2='dict')
    def get_equations(self, symbols_segment_1: dict, symbols_segment_2: dict):
        # TODO
        pass


class SegmentsPerpendicular(Restriction, ReferencedToObjects):
    _object_types = [Segment, Segment]

    @contract(symbols_segment_1='dict', symbols_segment_2='dict')
    def get_equations(self, symbols_segment_1: dict, symbols_segment_2: dict):
        # TODO
        pass


# Point and Segment

class PointFixedOnSegment(Restriction, ReferencedToObjects):
    _object_types = [Point, Segment]

    @contract(ratio='number,>0,<1')
    def __init__(self, ratio: float):
        self._ratio = ratio

    @contract(symbols_point='dict', symbols_segment='dict')
    def get_equations(self, symbols_point: dict, symbols_segment: dict):
        # TODO
        pass


class PointOnSegmentLine(Restriction, ReferencedToObjects):
    _object_types = [Point, Segment]

    @contract(symbols_point='dict', symbols_segment='dict')
    def get_equations(self, symbols_point: dict, symbols_segment: dict):
        # TODO
        pass


class PointAndSegmentStartJoint(Restriction, ReferencedToObjects):
    _object_types = [Point, Segment]

    @contract(symbols_point='dict', symbols_segment='dict')
    def get_equations(self, symbols_point: dict, symbols_segment: dict):
        # TODO
        pass


class PointAndSegmentEndJoint(Restriction, ReferencedToObjects):
    _object_types = [Point, Segment]

    @contract(symbols_point='dict', symbols_segment='dict')
    def get_equations(self, symbols_point: dict, symbols_segment: dict):
        # TODO
        pass


class PointAndSegmentCenterJoint(Restriction, ReferencedToObjects):
    _object_types = [Point, Segment]

    @contract(symbols_point='dict', symbols_segment='dict')
    def get_equations(self, symbols_point: dict, symbols_segment: dict):
        # TODO
        pass
