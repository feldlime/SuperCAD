import pytest
from numpy import isclose, pi
import numpy.random as random
from bindings import *
from figures import Figure

from figures import Figure, Point, Segment
from utils import (
    IncorrectParamType,
    IncorrectParamValue,
    IncorrectParamError
)
# TODO:


# noinspection PyTypeChecker
class TestBindings:
    def test_create_bindings(self):
        dict_figures = {}
        iterator = 0
        for coo in random.random((10, 2)) * 100 - 50:
            iterator += 1
            p = Point((coo[0], coo[1]))
            dict_figures["fig " + str(iterator)] = p
        b = create_bindings(dict_figures, circle_bindings_radius=8,
                            segment_bindings_margin=2)

