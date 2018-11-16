"""Module of OpenGL widget"""
from math import sqrt, pow

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QMainWindow
from figures import Point, Segment


class GLWindowProcessor:
    def __init__(self, plane):
        # noinspection PyArgumentList

        self._plane = plane
        self._painter = QPainter()

        # def paintEvent(self, event):
    #     painter = QPainter()
    #     painter.begin(self)
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     self.painter.paint(painter,
    #                        event,
    #                        self.center_width,
    #                        self.center_height,
    #                        self.segments_array,
    #                        self.points_array,
    #                        self.segments_array_view,
    #                        self.points_array_view,
    #                        self.mouse_xy)
    #     painter.end()
    #
    # # Отслеживание передвижения мыши
    # def mouseMoveEvent(self, event):
    #     # На каком расстоянии от мышки, объект будет выделяться
    #     near_size = 8
    #
    #     # Convert mouse coordinats to drawing space
    #     self.mouse_xy[0] = x = event.x() - self.center_width
    #     self.mouse_xy[1] = y = event.y() - self.center_height
    #
    #     self.points_array_view = self.points_array
    #     self.segments_array_view = self.segments_array
    #
    #     # TODO: Для полчучения привязок
    #     # project.get_bindings -> bindings.get_best_bindings
    #     # TODO: Для подсветки анализируем класс привязки и вызываем
    #     # bindings.object.bind
    #     # TODO: Для получения фигуры
    #     # bindinsg.object.get_object_names -> список имен объектов
    #     # project.get_figure(object_name) -> object_figure
    #
    #     if not self._window.Line_widget.isHidden():
    #         if len(self.now_drawing) > 0:
    #             s = Segment.from_points(self.now_drawing[0][0],
    #                                     self.now_drawing[0][1],
    #                                     x,
    #                                     y)
    #             self.segments_array_view.append(s)
    #         else:
    #             p = Point.from_coordinates(x, y)
    #             self.points_array_view.append(p)
    #
    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         x, y = self.mouse_xy
    #         self.now_drawing.append([x, y])
    #
    #         if not self._window.Point_widget.isHidden():
    #             p = Point.from_coordinates(x, y)
    #             self.points_array.append(p)
    #             self.now_drawing = []
    #
    #         if not self._window.Line_widget.isHidden() and len(
    #                 self.now_drawing) > 0:
    #             s = Segment.from_points(self.now_drawing[0][0],
    #                                     self.now_drawing[0][1],
    #                                     self.now_drawing[1][0],
    #                                     self.now_drawing[1][1])
    #             self.segments_array.append(s)
    #             self.now_drawing = []
