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
              bindings: List[Binding], mouse_xy: Tuple[int,int],
              center_xy: Tuple[int], rect: QRect):
    module_logger.debug('paint_all start')

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
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            painter.drawEllipse(*to_draw, 2, 2)
        elif isinstance(figure, Segment):
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            painter.drawLine(*to_draw)
        else:
            raise RuntimeError(f'Unexpected figure type {type(figure)}.')

    # Draw bindings
    for binding in bindings:
        if isinstance(binding, (PointBinding, SegmentStartBinding,
                                SegmentCenterBinding, SegmentEndBinding)):
            painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
            x, y = binding.bind()
            painter.drawEllipse(x, y, 4, 4)
        elif isinstance(binding, SegmentsIntersectionBinding):
            painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
            x, y = binding.bind()
            painter.drawEllipse(x, y, 4, 4)

            painter.setPen(QPen(Qt.cyan, 1, Qt.SolidLine))
            for name in binding.get_object_names():
                segment = figures[name]
                x1, y1, _, _ = segment.get_base_representation()
                painter.drawLine(x1, y1, x, y)
        elif isinstance(binding, FullSegmentBinding):
            painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
            segment = figures[binding.get_object_names()[0]]
            painter.drawLine(segment.get_base_representation())
        else:
            raise RuntimeError(f'Unexpected binding type {type(binding)}.')


def paint_line(painter: QPainter,
               line_point1: Tuple[int, int],
               mouse_xy: Tuple[int,int]):
    module_logger.debug('paint_line')

    painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
    # Draw line
    x1, y1 = line_point1
    x, y = mouse_xy
    painter.drawLine(x1, y1, x, y)

