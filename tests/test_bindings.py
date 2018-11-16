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
    def test_normal_creation(self):
        f = Figure((1, 2), 1)
        fisg = [f]
        b = Binding(fisg, circle_bindings_radius=8, segment_bindings_margin=2)