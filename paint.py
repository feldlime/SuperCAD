from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
import logging
from typing import Tuple, List, Dict
from figures import Figure, Point, Segment
from bindings import (
    Binding,
    PointBinding,
    SegmentSpotBinding,
    SegmentsIntersectionBinding,
    FullSegmentBinding
)

module_logger = logging.getLogger('paint.py')


def paint_all(painter: QPainter, figures: Dict[str, Figure],
              bindings: List[Binding], mouse_xy: Tuple[int, int]):
    # module_logger.debug('paint_all start')

    # Write coordinates near the mouse
    painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
    painter.drawText(
        QPointF(mouse_xy[0] + 15, -mouse_xy[1] - 10),
        f'{mouse_xy[0]}, {mouse_xy[1]}'
    )

    # Draw figures
    for figure in figures.values():
        to_draw = figure.get_base_representation()
        if isinstance(figure, Point):
            paint_point(painter, to_draw, 4, Qt.darkCyan)
        elif isinstance(figure, Segment):
            paint_segment(painter, to_draw, 2, Qt.darkBlue)
        else:
            raise RuntimeError(f'Unexpected figure type {type(figure)}.')

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


def paint_point(painter: QPainter, xy: Tuple[int, int], size: int, color):
    xy = to_display_xy(xy)
    painter.setPen(QPen(color, size // 2 + 1, Qt.SolidLine))
    painter.drawEllipse(xy[0] - size // 2,
                        xy[1] - size // 2,
                        size, size)


def paint_segment(
        painter: QPainter,
        coordinates: Tuple[int, int, int, int],  # x1, y1, x2, y2
        width: int,
        color
):
    coordinates = to_display_xy(coordinates)
    painter.setPen(QPen(color, width, Qt.SolidLine))
    painter.drawLine(*coordinates)


def to_display_xy(xy: tuple):
    if len(xy) == 2:
        return xy[0], -xy[1]
    elif len(xy) == 4:
        return xy[0], -xy[1], xy[2], -xy[3]

