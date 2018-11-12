from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QBrush, QColor, QPen


class Painter(object):
    def __init__(self):
        self.point_end = [0, 0]
        self.point_start = [0, 0]

    def paint(self, painter, event, center_width, center_height, segments_array,
              points_array, segments_array_view,
              points_array_view, mouse_xy):
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255)))
        # Настраиваем кисть
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.save()
        painter.translate(center_width, center_height)

        # Рисуем координаты рядом с мышкой
        painter.drawText(QPointF(mouse_xy[0] + 15, mouse_xy[1] + 10),
                         str(mouse_xy[0]) + 'x' + str(mouse_xy[1] * (-1)))

        # TODO: Для полчучения привязок
        # project.get_bindings -> bindings.get_best_bindings
        # TODO: Для подсветки анализируем класс привязки и вызываем
        # bindings.object.bind
        # TODO: Для получения фигуры
        # bindinsg.object.get_object_names -> список имен объектов
        # project.get_figure(object_name) -> object_figure


        # Рисуем все линии
        for line in segments_array:
            to_draw = line.get_base_representation()
            painter.drawLine(*to_draw)

        # Рисуем все точки
        for point in points_array:
            to_draw = point.get_base_representation()
            painter.drawEllipse(*to_draw, 2, 2)

        # Рисуем выделенные линии и точки
        painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
        for line in segments_array_view:
            to_draw = line.get_base_representation()
            painter.drawLine(*to_draw)
            painter.drawEllipse(QPointF(to_draw[0], to_draw[1]), 4, 4)
            painter.drawEllipse(QPointF(to_draw[2], to_draw[3]), 4, 4)

        for point in points_array_view:
            to_draw = point.get_base_representation()
            painter.drawEllipse(*to_draw, 4, 4)

        painter.restore()
