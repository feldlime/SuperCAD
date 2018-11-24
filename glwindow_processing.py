"""Module of OpenGL widget"""
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPaintEvent

import logging
from typing import Dict, Tuple, List

import paint

from figures import Figure, Point, Segment
from bindings import (
    Binding,
    PointBinding,
    SegmentStartBinding,
    SegmentCenterBinding,
    SegmentEndBinding,
    SegmentsIntersectionBinding,
    FullSegmentBinding,
    choose_best_bindings
)


class GLWindowProcessor:
    def __init__(self, glwindow):
        self._logger = logging.getLogger('GLWindowProcessor')

        # noinspection PyArgumentList
        self._glwindow = glwindow

        # Additional private attributes
        self._mouse_xy = (0, 0)
        self._last_clicked_point = (0, 0)  # x, y
        self._highlighted_figures_names = []

    def setup(self, width, height):
        self._logger.debug('setup start')

        self._glwindow.elapsed = 0

        self._glwindow.setAutoFillBackground(True)
        self._glwindow.setMouseTracking(True)

        # Располагаем виджет в области work_plane и присваеваем ему те же
        # параметры как в design
        self._glwindow.setGeometry(QtCore.QRect(0, 0, width, height))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self._glwindow.sizePolicy().hasHeightForWidth())

        self._glwindow.setSizePolicy(sizePolicy)

    @property
    def center(self) -> tuple:
        return self._glwindow.width() // 2, self._glwindow.height() // 2

    def paint_all(self, event: QPaintEvent, figures: Dict[str, Figure]):
        # self._logger.debug('paint_all start')
        painter = QPainter()
        painter.begin(self._glwindow)
        painter.setRenderHint(QPainter.Antialiasing)

        figures_with_styles = []
        for name, figure in figures.items():
            if name not in self._highlighted_figures_names:
                figures_with_styles.append((figure, 'basic'))
            else:
                figures_with_styles.append((figure, 'highlighted'))

        paint.paint_all(painter,
                        figures_with_styles,
                        self._mouse_xy,
                        self.center,
                        event.rect())
        painter.end()

    def _to_real_xy(self, x, y) -> tuple:
        return x - self.center[0], y - self.center[1]

    def handle_mouse_move_event(
            self, event, bindings: List[Binding], figures: Dict[str, Figure]):
        self._logger.debug('handle_mouse_move_event start')

        # Convert mouse coordinates to drawing space
        x, y = self._to_real_xy(event.x(), event.y())
        self._mouse_xy = (x, y)

        self._logger.debug(f'bindings: {bindings}')
        best_bindings = choose_best_bindings(bindings, x, y)

        # TODO: Для подсветки анализируем класс привязки и вызываем
        # bindings.object.bind
        # TODO: Для получения фигуры
        # bindinsg.object.get_object_names -> список имен объектов
        # project.get_figure(object_name) -> object_figure

        # if not self._window.Line_widget.isHidden():
        #     if len(self.now_drawing) > 0:
        #         s = Segment.from_points(self.now_drawing[0][0],
        #                                 self.now_drawing[0][1],
        #                                 x,
        #                                 y)
        #         self.segments_array_view.append(s)
        #     else:
        #         p = Point.from_coordinates(x, y)
        #         self.points_array_view.append(p)

    def handle_mouse_release_event(self, event):

        if event.button() == Qt.LeftButton:
            x, y = self._mouse_xy
            # self.now_drawing.append([x, y])
            #
            # if not self._window.Point_widget.isHidden():
            #     p = Point.from_coordinates(x, y)
            #     self.points_array.append(p)
            #     self.now_drawing = []
            #
            # if not self._window.Line_widget.isHidden() and len(
            #         self.now_drawing) > 0:
            #     s = Segment.from_points(self.now_drawing[0][0],
            #                             self.now_drawing[0][1],
            #                             self.now_drawing[1][0],
            #                             self.now_drawing[1][1])
            #     self.segments_array.append(s)
            #     self.now_drawing = []
