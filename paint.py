from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPen, QPainter
import logging
from typing import Tuple, List, Dict
from figures import Figure, Point, Segment
from bindings import (
    Binding,
    PointBinding,
    SegmentSpotBinding,
    SegmentsIntersectionBinding,
    FullSegmentBinding,
)

module_logger = logging.getLogger('paint.py')


def write_coordinates_near_pointer(painter, mouse_xy):
    painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
    xy = to_display_xy(mouse_xy)
    painter.drawText(
        QPointF(xy[0] + 15, xy[1] - 10), f'{mouse_xy[0]}, {mouse_xy[1]}'
    )


def paint_bindings(
    painter: QPainter, figures: Dict[str, Figure], bindings: List[Binding]
):

    # Draw bindings
    for binding in bindings:
        if isinstance(binding, PointBinding):
            paint_point(painter, binding.bind(), 6, Qt.cyan)
        elif isinstance(binding, SegmentSpotBinding):
            paint_point(painter, binding.bind(), 6, Qt.blue)
        elif isinstance(binding, SegmentsIntersectionBinding):
            x, y = binding.bind()
            paint_point(painter, (x, y), 6, Qt.magenta)
            for name in binding.get_object_names():
                segment = figures[name]
                x1, y1, _, _ = segment.get_base_representation()
                paint_segment(painter, (x1, y1, x, y), 1, Qt.magenta)
        elif isinstance(binding, FullSegmentBinding):
            seg = figures[binding.get_object_names()[0]]
            paint_segment(painter, seg.get_base_representation(), 3, Qt.blue)
        else:
            raise RuntimeError(f'Unexpected binding type {type(binding)}.')


def paint_figure(painter: QPainter, figure: Figure, style: str):
    """Paint points and segments.
    Style may be 'basic', 'selected' or 'created'.
    """

    coo = figure.get_base_representation()
    if isinstance(figure, Point):
        if style == 'basic':
            paint_point(painter, coo, 5, Qt.darkCyan)
        elif style == 'selected':
            paint_point(painter, coo, 6, Qt.cyan)
        elif style == 'created':
            paint_point(painter, coo, 6, Qt.green)
    elif isinstance(figure, Segment):
        if style == 'basic':
            paint_segment(painter, coo, 2, Qt.darkBlue)
        elif style == 'selected':
            paint_segment(painter, coo, 3, Qt.blue)
        elif style == 'created':
            paint_segment(painter, coo, 3, Qt.green)
    else:
        raise RuntimeError(f'Unexpected figure type {type(figure)}')


def paint_point(painter: QPainter, xy: Tuple[int, int], size: int, color):
    xy = to_display_xy(xy)
    painter.setPen(QPen(color, size // 2 + 1, Qt.SolidLine))
    painter.drawEllipse(xy[0] - size // 2, xy[1] - size // 2, size, size)


def paint_segment(
    painter: QPainter,
    coo: Tuple[int, int, int, int],  # x1, y1, x2, y2
    width: int,
    color,
):
    coo = [*to_display_xy(coo[:2]), *to_display_xy(coo[2:])]
    painter.setPen(QPen(color, width, Qt.SolidLine))
    painter.drawLine(*coo)


def to_display_xy(xy: Tuple[int, int]):
    return xy[0], -xy[1]
