"""Module with classes of geometry bindings."""

import numpy as np
from itertools import combinations
from contracts import contract

from utils import segment_length, ReferencedToObjects, BIG_DISTANCE
from figures import Point, Segment


def is_any_segment_binding(binding):
    return isinstance(binding, (SegmentSpotBinding, FullSegmentBinding))


def is_normal_point_binding(binding):
    return isinstance(binding, (SegmentSpotBinding, PointBinding))


def is_any_normal_binding(binding):
    return isinstance(
        binding, (SegmentSpotBinding, FullSegmentBinding, PointBinding)
    )


class Binding:
    """Class of binding."""

    def __init__(self, *args):
        pass

    @contract(x='number', y='number', returns='float|None')
    def check(self, x, y):
        """Check if given coordinates places in zone of binding.

        Parameters
        ----------
        x, y: int or float
            Coordinates of cursor.

        Returns
        ------
        checking_result: float or None
            None if cursor is out of binding zone.
            Distance between cursor and point of binding.
        """
        raise NotImplementedError

    @contract(returns='tuple(number, number)')
    def bind(self, *args):
        """ Return coordinates to bind cursor.

        Returns
        ------
        x, y: float
            Coordinates to bind.
        """
        raise NotImplementedError


class CentralBinding(Binding):
    """Class of binding with concrete point to bind."""

    def __init__(self, *args):
        super().__init__(*args)

    @contract(x='number', y='number', returns='float|None')
    def check(self, x, y):
        """Check if given coordinates places in zone of binding.

        Parameters
        ----------
        x, y: int or float
            Coordinates of cursor.

        Returns
        ------
        checking_result: float or None
            None if cursor is out of binding zone.
            Distance between cursor and point of binding.
        """
        raise NotImplementedError

    @contract(returns='tuple(number, number)')
    def bind(self):
        """ Return coordinates to bind cursor.

        Returns
        ------
        x, y: float
            Coordinates to bind
        """
        return self._coordinates()

    def _coordinates(self):
        """Return coordinates of binding."""
        raise NotImplementedError


class CircleBinding(CentralBinding):
    """Central binding with circle binding zone.

    Parameters
    ----------
    radius: int or float
        Radius of zone to bind.
    """

    @contract(radius='number, >0')
    def __init__(self, radius, *args):
        super().__init__(*args)

        self._radius = radius

    @contract(x='number', y='number', returns='float|None')
    def check(self, x, y):
        """Check if given coordinates places in zone of binding.

        Parameters
        ----------
        x, y: int or float
            Coordinates of cursor.

        Returns
        -------
        checking_result: float or None
            None if cursor is out of binding zone.
            Distance between cursor and point of binding.
        """
        base_x, base_y = self._coordinates()
        distance = segment_length(x, y, base_x, base_y)
        if distance > self._radius:
            return None
        else:
            return distance

    def _coordinates(self):
        """Return coordinates of binding."""
        raise NotImplementedError


class PointBinding(CircleBinding, ReferencedToObjects):
    """Point central binding with circle binding zone.

    Parameters
    ----------
    radius: int or float
        Radius of zone to bind.
    point: Point
        Point for binding.
    """

    _n_objects = 1

    @contract(radius='number, >0', point='$Point')
    def __init__(self, radius, point):
        super().__init__(radius)
        if not isinstance(point, Point):
            raise TypeError(f'Given object has type {type(point)}, not Point')
        self._point = point

    def _coordinates(self):
        """Return coordinates of binding."""
        return self._point.get_base_representation()


class SegmentSpotBinding(CircleBinding, ReferencedToObjects):
    """Central binding to spot of segment with circle binding zone.

    Parameters
    ----------
    radius: int or float
        Radius of zone to bind.
    segment: Segment
        Segment for binding.
    spot_type: {'start', 'end', 'center'}
    """

    _n_objects = 1

    @contract(radius='number, >0', segment='$Segment', spot_type='str')
    def __init__(self, radius, segment: Segment, spot_type: str):
        super().__init__(radius)

        if not isinstance(segment, Segment):
            raise TypeError(
                f'Given object has type {type(segment)}, not Segment'
            )
        self._segment = segment

        if spot_type not in ('start', 'end', 'center'):
            raise ValueError(f'Incorrect spot_type {spot_type}.')
        self._spot_type = spot_type

    @property
    def spot_type(self):
        return self._spot_type

    def _coordinates(self):
        """Return coordinates of binding."""
        x1, y1, x2, y2 = self._segment.get_base_representation()
        if self._spot_type == 'start':
            return x1, y1
        elif self._spot_type == 'end':
            return x2, y2
        else:  # center
            return (x1 + x2) / 2, (y1 + y2) / 2


class SegmentsIntersectionBinding(CircleBinding, ReferencedToObjects):
    """Central binding to segments intersection with circle binding zone.

    Parameters
    ----------
    radius: int or float
        Radius of zone to bind.
    segment1: Segment
        First segment of intersection for binding.
    segment2: Segment
        Second segment of intersection for binding.
    """

    _n_objects = 2

    @contract(radius='number, >0', segment1='$Segment', segment2='$Segment')
    def __init__(self, radius, segment1, segment2):
        super().__init__(radius)
        if not isinstance(segment1, Segment):
            raise TypeError(
                f'Given segment1 has type {type(segment1)}, not Segment'
            )
        if not isinstance(segment2, Segment):
            raise TypeError(
                f'Given segment1 has type {type(segment2)}, not Segment'
            )
        self._segment1 = segment1
        self._segment2 = segment2

    @contract(x='number', y='number', returns='float|None')
    def check(self, x, y):
        """Check if given coordinates places in zone of binding.

        Parameters
        ----------
        x, y: int or float
            Coordinates of cursor.

        Returns
        -------
        checking_result: float or None
            None if cursor is out of binding zone or binding doesn't exist.
            Otherwise distance between cursor and point of binding.
        """
        coo = self._coordinates()
        if coo is None:
            return None

        base_x, base_y = coo
        distance = segment_length(x, y, base_x, base_y)
        if distance > self._radius:
            return None
        else:
            return distance

    def _coordinates(self):
        """Return coordinates of binding."""
        # See original code here:
        # https://stackoverflow.com/questions/3252194/numpy-and-line-intersections

        ax1, ay1, ax2, ay2 = self._segment1.get_base_representation()
        bx1, by1, bx2, by2 = self._segment2.get_base_representation()

        a1, a2 = np.array([ax1, ay1]), np.array([ax2, ay2])
        b1, b2 = np.array([bx1, by1]), np.array([bx2, by2])

        da = a2 - a1
        db = b2 - b1
        dp = a1 - b1
        dap = np.array([-da[1], da[0]])

        denominator = np.dot(dap, db)
        if np.isclose(denominator, 0):
            return None

        numerator = np.dot(dap, dp)
        intersection_coo = (numerator / denominator) * db + b1
        return tuple(intersection_coo)


class FullSegmentBinding(Binding, ReferencedToObjects):
    """Binding to all segment (not to point).

    Parameters
    ----------
    margin: int or float
        Margin of zone to bind (distance from segment to binding zone border).
    segment: Segment
        Segment for binding.
    """

    _n_objects = 1

    @contract(margin='number, >0', segment='$Segment')
    def __init__(self, margin, segment):
        super().__init__()
        self._margin = margin
        if not isinstance(segment, Segment):
            raise TypeError(
                f'Given object has type {type(segment)}, not Segment'
            )
        self._segment = segment

    @contract(x='number', y='number', returns='float|None')
    def check(self, x, y):
        """Check if given coordinates places in zone of binding.

        Parameters
        ----------
        x, y: int or float
            Coordinates of cursor.

        Returns
        -------
        checking_result: int or bool
            None if cursor is out of binding zone.
            Distance between cursor and point of binding.
        """
        x1, y1, x2, y2 = self._segment.get_base_representation()
        distance = self._get_min_distance(x1, y1, x2, y2, x, y)

        if distance > self._margin:
            return None
        else:
            return distance

    @contract(x='number', y='number', returns='tuple(number, number)')
    def bind(self, x, y):
        """ Return coordinates to bind cursor.

        Parameters
        ----------
        x, y: int or float
            Coordinates of cursor.

        Returns
        ------
        x, y: float
            Coordinates to bind.
        """
        x1, y1, x2, y2 = self._segment.get_base_representation()
        return self._get_nearest_point(x1, y1, x2, y2, x, y)

    @classmethod
    def _get_min_distance(cls, x1, y1, x2, y2, x, y):
        """Calculate minimal distance from point to segment."""

        nearest_x, nearest_y = cls._get_nearest_point(x1, y1, x2, y2, x, y)
        _dx = nearest_x - x
        _dy = nearest_y - y
        square_dist = _dx ** 2 + _dy ** 2
        return np.sqrt(square_dist)

    @classmethod
    def _get_nearest_point(cls, x1, y1, x2, y2, x, y):
        """Calculate point at the segment that are the nearest to the given
        point.
        """
        dx = x2 - x1
        dy = y2 - y1
        dr2 = dx ** 2 + dy ** 2

        lerp = ((x - x1) * dx + (y - y1) * dy) / dr2
        if lerp < 0:
            lerp = 0
        elif lerp > 1:
            lerp = 1

        nearest_x = lerp * dx + x1
        nearest_y = lerp * dy + y1

        return nearest_x, nearest_y


@contract(bindings='list', x='number', y='number', returns='list')
def choose_best_bindings(bindings: list, x, y) -> list:
    """Choose the nearest binding.
    Choose only if coordinates are in binding zone.

    Parameters
    ----------
    bindings: list of Binding instances
        List of bindings.
    x, y: float
        Coordinates to measure distance (usually, coordinates of cursor).

    Returns
    -------
    best_bindings: list[Binding]
        Nearest bindings to given coordinates.
        If no close bindings, list will be empty.
    """
    atol = 10 ** (-3)
    min_dist = np.inf
    best_bindings = []

    for binding in bindings:
        dist = binding.check(x, y)

        if dist is None:
            continue

        if isinstance(binding, FullSegmentBinding):
            dist += BIG_DISTANCE  # Prefer point bindings to segment
        if isinstance(binding, SegmentsIntersectionBinding):
            dist += BIG_DISTANCE // 2  # Prefer point bindings to segment

        if np.isclose(dist, min_dist, atol=atol):
            best_bindings.append(binding)
        elif dist < min_dist:
            min_dist = dist
            best_bindings = [binding]

    return best_bindings


@contract(
    figures='dict[N]',
    circle_bindings_radius='number, >0',
    segment_bindings_margin='number, >0',
    returns='list[>=N]',
)
def create_bindings(
    figures: dict, circle_bindings_radius=8, segment_bindings_margin=2
) -> list:
    """Create all bindings for all figures.

    Parameters
    ----------
    figures: dict
        Dictionary of all figures to create bindings.
    circle_bindings_radius: int or float, optional, default 8
        Radius of binding zone for circle bindings.
    segment_bindings_margin: int or float
        Margin of binding zone for full segment bindings.

    Returns
    -------
    bindings: list
        List of bindings.
    """

    segments = dict()  # For SegmentsIntersectionsBinding
    bindings = []

    for name, figure in figures.items():
        if isinstance(figure, Point):
            binding = PointBinding(circle_bindings_radius, figure)
            binding.set_object_names([name])
            bindings.append(binding)

        elif isinstance(figure, Segment):
            binding = SegmentSpotBinding(
                circle_bindings_radius, figure, spot_type='start'
            )
            binding.set_object_names([name])
            bindings.append(binding)

            binding = SegmentSpotBinding(
                circle_bindings_radius, figure, spot_type='end'
            )
            binding.set_object_names([name])
            bindings.append(binding)

            binding = SegmentSpotBinding(
                circle_bindings_radius, figure, spot_type='center'
            )
            binding.set_object_names([name])
            bindings.append(binding)

            # Segment full
            binding = FullSegmentBinding(segment_bindings_margin, figure)
            binding.set_object_names([name])
            bindings.append(binding)

            # For intersection bindings
            segments[name] = figure

        else:
            TypeError(f'Incorrect type of figure: {type(figure)}')

    # Intersection bindings
    for (name1, segment1), (name2, segment2) in combinations(
        segments.items(), 2
    ):
        binding = SegmentsIntersectionBinding(
            circle_bindings_radius, segment1, segment2
        )
        binding.set_object_names([name1, name2])
        bindings.append(binding)

    return bindings
