"""Module with classes of geometry restrictions."""

# noinspection PyUnresolvedReferences
from numpy import pi as np_pi, sign as np_sign, tan as np_tan, cos as np_cos
from sympy import Eq, sign as sp_sign, sqrt as sp_sqrt
from contracts import contract

from utils import (
    ReferencedToObjects,
    IncorrectParamValue,
    simplify_angle
)
from figures import Point, Segment


class Restriction:
    """Base restriction class."""
    object_types = []

    def __init__(self):
        pass

    @property
    def _n_objects(self):
        return len(self.object_types)

    def get_equations(self, *args) -> list:
        raise NotImplementedError


# Point

class PointFixed(Restriction, ReferencedToObjects):
    object_types = [Point]

    @contract(x='number', y='number')
    def __init__(self, x, y):
        super().__init__()
        self._x = x
        self._y = y

    @contract(symbols='dict[2]')
    def get_equations(self, symbols: dict):
        x, y = symbols['x'], symbols['y']
        equations = [
            Eq(x, self._x),
            Eq(y, self._y)
        ]
        return equations


# Two points

class PointsJoint(Restriction, ReferencedToObjects):
    object_types = [Point, Point]

    @contract(symbols_point_1='dict[2]', symbols_point_2='dict[2]')
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
    object_types = [Segment]

    @contract(x1='number', y1='number', x2='number', y2='number')
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

    @contract(symbols='dict[4]')
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


class SegmentSpotFixed(Restriction, ReferencedToObjects):
    object_types = [Segment]

    @contract(x='number', y='number', spot_type='str')
    def __init__(self, x, y, spot_type):
        super().__init__()
        self._x = x
        self._y = y

        if spot_type not in ('start', 'end', 'center'):
            raise IncorrectParamValue(f'Incorrect spot_type {spot_type}.')
        self._spot_type = spot_type

    @contract(symbols='dict[4]')
    def get_equations(self, symbols: dict):
        x1, y1 = symbols['x1'], symbols['y1']
        x2, y2 = symbols['x2'], symbols['y2']

        if self._spot_type == 'start':
            equations = [
                Eq(x1, self._x),
                Eq(y1, self._y)
            ]
        elif self._spot_type == 'end':
            equations = [
                Eq(x2, self._x),
                Eq(y2, self._y)
            ]
        else:  # center
            equations = [
                Eq((x1 + x2) / 2, self._x),
                Eq((y1 + y2) / 2, self._y)
            ]

        return equations


class SegmentLengthFixed(Restriction, ReferencedToObjects):
    object_types = [Segment]

    @contract(length='number, >0')
    def __init__(self, length):
        super().__init__()
        self._length = length

    @contract(symbols='dict[4]')
    def get_equations(self, symbols: dict):
        x1, y1 = symbols['x1'], symbols['y1']
        x2, y2 = symbols['x2'], symbols['y2']
        equations = [
            Eq((x2 - x1) ** 2 + (y2 - y1) ** 2, self._length ** 2)
        ]
        return equations


class SegmentAngleFixed(Restriction, ReferencedToObjects):
    object_types = [Segment]

    @contract(angle='number, > 0, < 2 * $np_pi')
    def __init__(self, angle):
        super().__init__()
        self._angle = angle

    @contract(symbols='dict[4]')
    def get_equations(self, symbols: dict):
        x1, y1 = symbols['x1'], symbols['y1']
        x2, y2 = symbols['x2'], symbols['y2']

        sign = np_sign(simplify_angle(self._angle) - np_pi)
        equations = [
            Eq((y2 - y1), (x2 - x1) * np_tan(self._angle)),
            Eq(sp_sign(y2 - y1), sign)  # TODO: Maybe drop?
        ]
        return equations


class SegmentHorizontal(Restriction, ReferencedToObjects):
    object_types = [Segment]

    @contract(symbols='dict[4]')
    def get_equations(self, symbols: dict):
        x1, y1 = symbols['x1'], symbols['y1']
        x2, y2 = symbols['x2'], symbols['y2']
        equations = [
            Eq(y1, y2)
        ]
        return equations


class SegmentVertical(Restriction, ReferencedToObjects):
    object_types = [Segment]

    @contract(symbols='dict[4]')
    def get_equations(self, symbols: dict):
        x1, y1 = symbols['x1'], symbols['y1']
        x2, y2 = symbols['x2'], symbols['y2']
        equations = [
            Eq(x1, x2)
        ]
        return equations


# Segments

class SegmentsAngleBetweenFixed(Restriction, ReferencedToObjects):
    object_types = [Segment, Segment]

    @contract(angle='number, > 0, < 2 * $np_pi')
    def __init__(self, angle):
        super().__init__()
        self._angle = angle

    @contract(symbols_segment_1='dict[4]', symbols_segment_2='dict[4]')
    def get_equations(self, symbols_segment_1: dict, symbols_segment_2: dict):
        s1_x1, s1_y1 = symbols_segment_1['x1'], symbols_segment_1['y1']
        s1_x2, s1_y2 = symbols_segment_1['x2'], symbols_segment_1['y2']
        s2_x1, s2_y1 = symbols_segment_2['x1'], symbols_segment_2['y1']
        s2_x2, s2_y2 = symbols_segment_2['x2'], symbols_segment_2['y2']

        s1_dx, s1_dy = s1_x2 - s1_x1, s1_y2 - s1_y1
        s2_dx, s2_dy = s2_x2 - s2_x1, s2_y2 - s2_y1

        scalar_prod = s1_dx * s2_dx + s1_dy * s2_dy
        l1 = sp_sqrt(s1_dx ** 2 + s1_dy ** 2)
        l2 = sp_sqrt(s2_dx ** 2 + s2_dy ** 2)

        equations = [
            Eq(scalar_prod, l1 * l2 * np_cos(self._angle))  # TODO: simplify?
        ]
        return equations


class SegmentsParallel(Restriction, ReferencedToObjects):
    object_types = [Segment, Segment]

    @contract(symbols_segment_1='dict[4]', symbols_segment_2='dict[4]')
    def get_equations(self, symbols_segment_1: dict, symbols_segment_2: dict):
        s1_x1, s1_y1 = symbols_segment_1['x1'], symbols_segment_1['y1']
        s1_x2, s1_y2 = symbols_segment_1['x2'], symbols_segment_1['y2']
        s2_x1, s2_y1 = symbols_segment_2['x1'], symbols_segment_2['y1']
        s2_x2, s2_y2 = symbols_segment_2['x2'], symbols_segment_2['y2']

        s1_dx, s1_dy = s1_x2 - s1_x1, s1_y2 - s1_y1
        s2_dx, s2_dy = s2_x2 - s2_x1, s2_y2 - s2_y1
        equations = [
            Eq(s1_dy * s2_dx - s2_dy * s1_dx, 0)  # vector product is 0
        ]
        return equations


class SegmentsNormal(Restriction, ReferencedToObjects):
    object_types = [Segment, Segment]

    @contract(symbols_segment_1='dict[4]', symbols_segment_2='dict[4]')
    def get_equations(self, symbols_segment_1: dict, symbols_segment_2: dict):
        s1_x1, s1_y1 = symbols_segment_1['x1'], symbols_segment_1['y1']
        s1_x2, s1_y2 = symbols_segment_1['x2'], symbols_segment_1['y2']
        s2_x1, s2_y1 = symbols_segment_2['x1'], symbols_segment_2['y1']
        s2_x2, s2_y2 = symbols_segment_2['x2'], symbols_segment_2['y2']

        s1_dx, s1_dy = s1_x2 - s1_x1, s1_y2 - s1_y1
        s2_dx, s2_dy = s2_x2 - s2_x1, s2_y2 - s2_y1
        equations = [
            Eq(s1_dx * s2_dx + s1_dy * s2_dy, 0)  # Scalar product is 0
        ]
        return equations


class SegmentsSpotsJoint(Restriction, ReferencedToObjects):
    object_types = [Segment, Segment]

    @contract(spot1_type='str', spot2_type='str')
    def __init__(self, spot1_type, spot2_type):
        super().__init__()

        if spot1_type not in ('start', 'end', 'center'):
            raise IncorrectParamValue(f'Incorrect spot1_type {spot1_type}.')
        self._spot1_type = spot1_type

        if spot2_type not in ('start', 'end', 'center'):
            raise IncorrectParamValue(f'Incorrect spot2_type {spot2_type}.')
        self._spot2_type = spot2_type

    @contract(symbols_segment_1='dict[4]', symbols_segment_2='dict[4]')
    def get_equations(self, symbols_segment_1: dict, symbols_segment_2: dict):
        s1_x1, s1_y1 = symbols_segment_1['x1'], symbols_segment_1['y1']
        s1_x2, s1_y2 = symbols_segment_1['x2'], symbols_segment_1['y2']
        s2_x1, s2_y1 = symbols_segment_2['x1'], symbols_segment_2['y1']
        s2_x2, s2_y2 = symbols_segment_2['x2'], symbols_segment_2['y2']

        if self._spot1_type == 'start':
            left_parts = [
                s1_x1,
                s1_y1
            ]
        elif self._spot1_type == 'end':
            left_parts = [
                s1_x2,
                s1_y2
            ]
        else:  # center
            left_parts = [
                (s1_x1 + s1_x2) / 2,
                (s1_y1 + s1_y2) / 2
            ]

        if self._spot2_type == 'start':
            right_parts = [
                s2_x1,
                s2_y1
            ]
        elif self._spot2_type == 'end':
            right_parts = [
                s2_x2,
                s2_y2
            ]
        else:  # center
            right_parts = [
                (s2_x1 + s2_x2) / 2,
                (s2_y1 + s2_y2) / 2
            ]

        equations = [
            Eq(left_parts[0], right_parts[0]),
            Eq(left_parts[1], right_parts[1])
        ]

        return equations


# Point and Segment

class PointOnSegmentFixed(Restriction, ReferencedToObjects):
    object_types = [Point, Segment]

    @contract(ratio='number, >0, <1')
    def __init__(self, ratio: float):
        self._ratio = ratio

    @contract(symbols_point='dict[2]', symbols_segment='dict[4]')
    def get_equations(self, symbols_point: dict, symbols_segment: dict):
        x, y = symbols_point['x'], symbols_point['y']
        x1, y1 = symbols_segment['x1'], symbols_segment['y1']
        x2, y2 = symbols_segment['x2'], symbols_segment['y2']

        dx, dy = x2 - x1, y2 - y1
        equations = [
            Eq(x, x1 + dx * self._ratio),
            Eq(y, y1 + dy * self._ratio),
        ]
        return equations


class PointOnSegmentLine(Restriction, ReferencedToObjects):
    object_types = [Point, Segment]

    @contract(symbols_point='dict[2]', symbols_segment='dict[4]')
    def get_equations(self, symbols_point: dict, symbols_segment: dict):
        x, y = symbols_point['x'], symbols_point['y']
        x1, y1 = symbols_segment['x1'], symbols_segment['y1']
        x2, y2 = symbols_segment['x2'], symbols_segment['y2']

        dx, dy = x2 - x1, y2 - y1

        equations = [
            Eq(dx * (y - y1) - (x - x1) * dy, 0)  # vector product is 0
        ]
        return equations


class PointAndSegmentSpotJoint(Restriction, ReferencedToObjects):
    object_types = [Point, Segment]

    @contract(spot_type='str')
    def __init__(self, spot_type):
        super().__init__()
        if spot_type not in ('start', 'end', 'center'):
            raise IncorrectParamValue(f'Incorrect spot_type {spot_type}.')
        self._spot_type = spot_type

    @contract(symbols_point='dict', symbols_segment='dict')
    def get_equations(self, symbols_point: dict, symbols_segment: dict):
        x, y = symbols_point['x'], symbols_point['y']
        x1, y1 = symbols_segment['x1'], symbols_segment['y1']
        x2, y2 = symbols_segment['x2'], symbols_segment['y2']

        if self._spot_type == 'start':
            equations = [
                Eq(x, x1),
                Eq(y, y1)
            ]
        elif self._spot_type == 'end':
            equations = [
                Eq(x, x2),
                Eq(y, y2)
            ]
        else:  # center
            equations = [
                Eq(x, (x1 + x2) / 2),
                Eq(y, (y1 + y2) / 2)
            ]

        return equations
