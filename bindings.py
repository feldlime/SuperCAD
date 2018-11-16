"""Module with classes of geometry bindings."""

from utils import (
    validate_positive_num,
    Coordinates,
    segment_length,
    ReferencedToObjects,
    BIG_DISTANCE,
)
from figures import Point, Segment

import numpy as np
from contracts import contract
from itertools import combinations


class Binding:
    """Class of binding."""

    def __init__(self, *args, **kwargs):
        pass

    def check(self, x, y):
        """Check if given coordinates places in zone of binding.

        Parameters
        ----------
        x, y: int or float
            Coordinates of cursor.

        Returns
        ------
        checking_result: int or bool
            False if cursor is out of binding zone.
            Distance between cursor and point of binding.
        """
        raise NotImplementedError

    def bind(self, *args):
        """ Return coordinates to bind cursor.

        Returns
        ------
        x, y: float
            Coordinates to bind
        """
        raise NotImplementedError


class CentralBinding(Binding):
    """Class of binding with concrete point to bind.

    Parameters
    ----------
    coordinates: tuple or function
        The object for which this binding is created.
        If tuple, it must be coordinates of point.
        If function, it must be function, that returns coordinates of point.
    """

    def __init__(self, coordinates, coordinates_kwargs=None, *args, **kwargs):
        super().__init__()
        if coordinates_kwargs is None:
            coordinates_kwargs = {}
        self._coordinates = Coordinates(coordinates, **coordinates_kwargs)

    def bind(self, *args):
        """ Return coordinates to bind cursor.

        Returns
        ------
        x, y: float
            Coordinates to bind
        """
        return self._coordinates.get()

    def check(self, x, y):
        """Check if given coordinates places in zone of binding.

        Parameters
        ----------
        x, y: int or float
            Coordinates of cursor.

        Returns
        ------
        checking_result: int or bool
            False if cursor is out of binding zone.
            Distance between cursor and point of binding.
        """
        raise NotImplementedError


class CircleBinding(CentralBinding):
    """Class of binding with circle zone.

    Parameters
    ----------
    coordinates: tuple or function
        The object for which this binding is created.
        If tuple, it must be coordinates of point.
        If function, it must be function, that returns coordinates of point.
    radius: int or float
        Radius of zone to bind.
    """

    def __init__(self, coordinates, radius, coordinates_kwargs=None):
        if coordinates_kwargs is None:
            coordinates_kwargs = {}
        super().__init__(coordinates, coordinates_kwargs=coordinates_kwargs)

        validate_positive_num(radius, 'radius')
        self._radius = radius

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
        base_x, base_y = self._coordinates.get()
        distance = segment_length(x, y, base_x, base_y)
        if distance > self._radius:
            return None
        else:
            return distance


class PointBinding(CircleBinding, ReferencedToObjects):
    _n_objects = 1
    pass


class SegmentStartBinding(CircleBinding, ReferencedToObjects):
    _n_objects = 1
    pass


class SegmentEndBinding(CircleBinding, ReferencedToObjects):
    _n_objects = 1
    pass


class SegmentCenterBinding(CircleBinding, ReferencedToObjects):
    _n_objects = 1
    pass


class SegmentsIntersectionBinding(CircleBinding, ReferencedToObjects):
    _n_objects = 2

    def __init__(self, coordinates, radius):
        coordinates_kwargs = {'allow_none': True}
        super().__init__(coordinates, radius,
                         coordinates_kwargs=coordinates_kwargs)

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
        coo = self._coordinates.get()
        if coo is None:
            return None

        base_x, base_y = coo
        distance = segment_length(x, y, base_x, base_y)
        if distance > self._radius:
            return None
        else:
            return distance


class FullSegmentBinding(Binding, ReferencedToObjects):
    """Binding to all segment (not to point) to highlight it."""
    _n_objects = 1

    def __init__(self, coordinates_1, coordinates_2, margin):
        super().__init__()
        self._coordinates_1 = Coordinates(coordinates_1)
        self._coordinates_2 = Coordinates(coordinates_2)
        validate_positive_num(margin, 'margin')
        self._margin = margin

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
        x1, y1 = self._coordinates_1.get()
        x2, y2 = self._coordinates_2.get()
        distance = self._get_min_distance(x1, y1, x2, y2, x, y)

        if distance > self._margin:
            return None
        else:
            return distance

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
        x1, y1 = self._coordinates_1.get()
        x2, y2 = self._coordinates_2.get()
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

        if np.isclose(dist, min_dist, atol=atol):
            best_bindings.append(binding)
        elif dist < min_dist:
            min_dist = dist
            best_bindings = [binding]

    return best_bindings


@contract(figures='dict[N]', circle_bindings_radius='number,>0',
          segment_bindings_margin='number,>0', returns='list[>=N]')
def create_bindings(figures: dict, circle_bindings_radius=8,
                    segment_bindings_margin=2) -> list:
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
            def point_coo():
                return figure.get_base_representation()
            binding = PointBinding(point_coo, circle_bindings_radius)
            binding.set_object_names(name)
            bindings.append(binding)

        elif isinstance(figure, Segment):
            def segment_start_coo():
                x1, y1, x2, y2 = figure.get_base_representation()
                return x1, y1
            binding = SegmentStartBinding(segment_start_coo,
                                          circle_bindings_radius)
            binding.set_object_names(name)
            bindings.append(binding)

            def segment_end_coo():
                x1, y1, x2, y2 = figure.get_base_representation()
                return x2, y1
            binding = SegmentEndBinding(segment_end_coo,
                                        circle_bindings_radius)
            binding.set_object_names(name)
            bindings.append(binding)

            def segment_center_coo():
                x1, y1, x2, y2 = figure.get_base_representation()
                return (x1 + x2) / 2, (y1 + y2) / 2
            binding = SegmentCenterBinding(segment_center_coo,
                                           circle_bindings_radius)
            binding.set_object_names(name)
            bindings.append(binding)

            # Segment full
            binding = FullSegmentBinding(segment_start_coo, segment_end_coo,
                                         segment_bindings_margin)
            binding.set_object_names(name)
            bindings.append(binding)

            # For intersection bindings
            segments[name] = figure

        else:
            TypeError(f'Incorrect type of figure: {type(figure)}')

    # Intersection bindings
    for (name1, segment1), (name2, segment2) \
            in combinations(segments.items(), 2):
        def segments_intersection_coo():
            # See original code here:
            # https://stackoverflow.com/questions/3252194/numpy-and-line-intersections

            ax1, ay1, ax2, ay2 = segment1.get_base_representation()
            bx1, by1, bx2, by2 = segment2.get_base_representation()

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
            return (numerator / denominator) * db + b1
        binding = SegmentsIntersectionBinding(segments_intersection_coo,
                                              circle_bindings_radius)
        binding.set_object_names([name1, name2])
        bindings.append(binding)

    return bindings
