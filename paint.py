from PyQt5.QtCore import QPointF, Qt, QRect
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
import logging
from typing import Tuple, List, Dict
from figures import Figure, Point, Segment
from bindings import (
    Binding,
    PointBinding,
    SegmentStartBinding,
    SegmentCenterBinding,
    SegmentEndBinding,
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
        QPointF(mouse_xy[0] + 15, mouse_xy[1] + 10),
        f'{mouse_xy[0]}, {mouse_xy[1] * (-1)}'
    )

    # Draw figures
    for figure in figures.values():
        to_draw = figure.get_base_representation()
        if isinstance(figure, Point):
            paint_point(painter, to_draw, 4, Qt.darkCyan)
        elif isinstance(figure, Segment):
            painter.setPen(QPen(Qt.darkBlue, 2, Qt.SolidLine))
            painter.drawLine(*to_draw)
        else:
            raise RuntimeError(f'Unexpected figure type {type(figure)}.')

    # Draw bindings
    for binding in bindings:
        if isinstance(binding, PointBinding):
            paint_point(painter, binding.bind(), 6, Qt.cyan)
        elif isinstance(binding, (SegmentStartBinding,
                                  SegmentCenterBinding, SegmentEndBinding)):
            paint_point(painter, binding.bind(), 6, Qt.blue)
        elif isinstance(binding, SegmentsIntersectionBinding):
            x, y = binding.bind()

            paint_point(painter, (x, y), 6, Qt.magenta)
            painter.setPen(QPen(Qt.magenta, 1, Qt.SolidLine))
            for name in binding.get_object_names():
                segment = figures[name]
                x1, y1, _, _ = segment.get_base_representation()
                painter.drawLine(x1, y1, x, y)
        elif isinstance(binding, FullSegmentBinding):
            painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
            segment = figures[binding.get_object_names()[0]]
            painter.drawLine(*segment.get_base_representation())
        else:
            raise RuntimeError(f'Unexpected binding type {type(binding)}.')


def paint_point(painter: QPainter, xy: Tuple[int, int], size: int, color):
    painter.setPen(QPen(color, size // 2 + 1, Qt.SolidLine))
    painter.drawEllipse(xy[0] - size // 2, xy[1] - size // 2, size, size)


def paint_line(painter: QPainter,
               line_point1: Tuple[int, int],
               mouse_xy: Tuple[int, int]):
    module_logger.debug('paint_line')

    painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
    # Draw line
    x1, y1 = line_point1
    x, y = mouse_xy
    painter.drawLine(x1, y1, x, y)

