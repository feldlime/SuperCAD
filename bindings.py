"""Module with classes of geometry bindings."""

from utils import (
    IncorrectParamType,
    validate_positive_num,
    validate_coordinates
)
from figures import Point, Segment


class BaseBinding:
    def check(self, x, y):
        raise NotImplemented


class Binding(BaseBinding):
    """Class of simple binding with circle zone.

    coordinates: tuple or function
        The object for which this binding is created.
        If tuple, it must be coordinates of point.
        If function, it must be function, that returns coordinates of point.
    """

    def __init__(self, coordinates, radius, **kwargs):
        if isinstance(coordinates, tuple):
            validate_coordinates(coordinates,
                                 'If coordinates is tuple, it must contain '
                                 '2 numbers.')

        elif isinstance(coordinates, function):
            test_coordinates = coordinates()
            validate_coordinates(test_coordinates,
                                 'If coordinates is function, it must returns'
                                 'tuple that contains 2 numbers.')

        else:
            raise IncorrectParamType('Coordinates must be tuple or function.')

        validate_positive_num(radius, 'radius')

        self._coordinates = coordinates
        self._radius_sqr = radius ** 2

    def check(self, x, y):
        """Check if given coordinates places in zone of binding.

        Parameters
        ----------
        x, y: int or float
            Coordinates of cursor.

        Return
        ------
        checking_result: int or bool
            False if cursor is out of binding zone.
            Distance between cursor and point of binding.
        """
        base_x, base_y = self._coordinates()
        distance_sqr = (x - base_x) ** 2 + (y - base_y) ** 2
        if distance_sqr > self._radius_sqr:
            return False
        else:
            return distance_sqr ** 0.5

    def _coordinates(self):
        if isinstance(self._coordinates, tuple):
            return self._coordinates
        else:
            return self._coordinates()


class ObjectBinding(Binding):
    def __init__(self, coordinates, radius, object_name):
        super().__init__(coordinates, radius)
        self.object_name = object_name


class PointBinding(ObjectBinding):
    pass


class SegmentStartBinding(ObjectBinding):
    pass


class SegmentEndBinding(ObjectBinding):
    pass


class SegmentCenterBinding(ObjectBinding):
    pass


class SegmentsIntersectionsBinding(Binding):
    def __init__(self, coordinates, radius, segment_1_name, segment_2_name):
        super().__init__(coordinates, radius)
        self.segment_1_name = segment_1_name
        self.segment_2_name = segment_2_name


