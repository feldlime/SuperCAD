from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QBrush, QColor, QPen


def paint_all(painter, figures, mouse_xy, rect):
    painter.fillRect(rect, QBrush(QColor(255, 255, 255)))
    # Настраиваем кисть
    # painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
    # painter.save()
    # painter.translate(center_width, center_height)

    # Рисуем координаты рядом с мышкой
    painter.drawText(QPointF(mouse_xy[0] + 15, mouse_xy[1] + 10),
                     str(mouse_xy[0]) + 'x' + str(mouse_xy[1] * (-1)))


    # Рисуем все линии
    # for line in segments_array:
    #     to_draw = line.get_base_representation()
    #     painter.drawLine(*to_draw)
    #
    # # Рисуем все точки
    # for point in points_array:
    #     to_draw = point.get_base_representation()
    #     painter.drawEllipse(*to_draw, 2, 2)
    #
    # # Рисуем выделенные линии и точки
    # painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
    # for line in segments_array_view:
    #     to_draw = line.get_base_representation()
    #     painter.drawLine(*to_draw)
    #     painter.drawEllipse(QPointF(to_draw[0], to_draw[1]), 4, 4)
    #     painter.drawEllipse(QPointF(to_draw[2], to_draw[3]), 4, 4)
    #
    # for point in points_array_view:
    #     to_draw = point.get_base_representation()
    #     painter.drawEllipse(*to_draw, 4, 4)

    painter.restore()
