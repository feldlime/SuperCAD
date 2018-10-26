"""Module with classes of geometry bindings."""

from utils import (
    validate_positive_num,
    Coordinates,
    magnitude
)

import numpy as np


class ReferencedToObject:
    """Interface for objects that are referenced to other object"""

    def set_object_name(self, object_name: str):
        """Set host object name."""
        self._object_name = object_name

    def get_object_name(self) -> str:
        """Get host object name."""
        return self._object_name


class ReferencedToObjects:
    """Interface for objects that are referenced to other object"""

    def set_object_names(self, object_names: list):
        """Set host object name."""
        self._object_names = object_names

    def get_object_names(self) -> list:
        """Get host object name."""
        return self._object_names


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

    def __init__(self, coordinates, *args, **kwargs):
        super().__init__()
        self._coordinates = Coordinates(coordinates)

    def bind(self, *args):
        """ Return coordinates to bind cursor.

        Returns
        ------
        x, y: float
            Coordinates to bind
        """
        return self._coordinates()

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

    def __init__(self, coordinates, radius):
        super().__init__(coordinates)

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
        checking_result: int or None
            None if cursor is out of binding zone.
            Distance between cursor and point of binding.
        """
        base_x, base_y = self._coordinates.get()
        distance = magnitude(x, y, base_x, base_y)
        if distance > self._radius:
            return False
        else:
            return distance


class PointBinding(CircleBinding, ReferencedToObject):
    pass


class SegmentStartBinding(CircleBinding, ReferencedToObject):
    pass


class SegmentEndBinding(CircleBinding, ReferencedToObject):
    pass


class SegmentCenterBinding(CircleBinding, ReferencedToObject):
    pass


class SegmentsIntersectionsBinding(CircleBinding, ReferencedToObjects):
    pass


class SegmentBinding(Binding, ReferencedToObject):
    """Binding to all segment (not to point) to highlight it."""
    def __init__(self, coordinates_1, coordinates_2, radius):
        super().__init__()
        self._coordinates_1 = Coordinates(coordinates_1)
        self._coordinates_2 = Coordinates(coordinates_2)
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
        checking_result: int or bool
            None if cursor is out of binding zone.
            Distance between cursor and point of binding.
        """
        x1, y1 = self._coordinates_1.get()
        x2, y2 = self._coordinates_2.get()
        distance = self._get_min_distance(x1, y1, x2, y2, x, y)

        if distance > self._radius:
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

        # TODO
        pass

    @classmethod
    def _get_nearest_point(cls, x1, y1, x2, y2, x, y):
        """Calculate point at the segment that are the nearest to the given
        point.
        """

        # TODO
        pass


def choose_best_binding(bindings: list, x, y):
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
    best_binding: Binding or None
        Nearest binding to given coordinates.
        None if no bindings near the coordinates.
    """
    if not bindings:
        return None

    def key_fun(binding):
        dist = binding.check(x, y)
        return dist if dist is not None else np.inf

    bindings = sorted(bindings, key=key_fun)
    best_binding = bindings[0] if not np.isinf(bindings[0]) else None
    return best_binding
