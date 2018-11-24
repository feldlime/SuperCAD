from PyQt5.QtCore import QPointF, Qt, QRect
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
import logging
from typing import Tuple, List
from figures import Figure, Point, Segment

module_logger = logging.getLogger('paint.py')


def paint_all(painter: QPainter, figures: List[Tuple[Figure, str]],
              mouse_xy: Tuple[int], center_xy: Tuple[int], rect: QRect):
    # module_logger.debug('paint_all start')
    painter.fillRect(rect, QBrush(QColor(255, 255, 255)))
    painter.save()
    painter.translate(*center_xy)

    # Рисуем координаты рядом с мышкой
    painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
    painter.drawText(
        QPointF(mouse_xy[0] + 15, mouse_xy[1] + 10),
        f'{mouse_xy[0]}, {mouse_xy[1] * (-1)}'
    )

    for figure, style in figures:
        to_draw = figure.get_base_representation()
        if style == 'basic':
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            if isinstance(figure, Point):
                painter.drawEllipse(*to_draw, 2, 2)
            elif isinstance(figure, Segment):
                painter.drawLine(*to_draw)
            else:
                raise RuntimeError(f'Unexpected figure type {type(figure)}.')
        elif style == 'highlighted':
            painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
            if isinstance(figure, Point):
                painter.drawEllipse(*to_draw, 4, 4)
            elif isinstance(figure, Segment):
                painter.drawLine(*to_draw)
            else:
                raise RuntimeError(f'Unexpected figure type {type(figure)}.')
        else:
            raise RuntimeError(f'Unexpected style {style}.')

    painter.restore()
