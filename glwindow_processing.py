"""Module of OpenGL widget"""
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPaintEvent

import logging
from typing import Dict, Tuple, List, Optional, Type

import paint

from states import ControllerWorkSt, ChooseSt, ControllerSt
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
        self._current_bindings = []

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

    def paint_all(self, event: QPaintEvent,
                  figures: Dict[str, Figure],
                  painted_figure: Optional[Figure] = None,
                  selected_figure: Optional[Figure] = None):
        # self._logger.debug('paint_all start')
        painter = QPainter()
        painter.begin(self._glwindow)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255)))
        painter.save()
        painter.translate(*self.center)

        # self._logger.debug(f'current_bindings: {self._current_bindings}')
        paint.paint_all(
            painter, figures, self._current_bindings, self._mouse_xy
        )

        # Paint painted figure
        if painted_figure is not None:
            coo = painted_figure.get_base_representation()
            if isinstance(painted_figure, Point):
                paint.paint_point(painter, coo, 6, Qt.green)
            elif isinstance(painted_figure, Segment):
                paint.paint_segment(painter, coo, 3, Qt.green)
            else:
                raise RuntimeError(
                    f'Unexpected figure type {type(painted_figure)}')

        # Paint selected figure
        if selected_figure is not None:
            coo = selected_figure.get_base_representation()
            if isinstance(selected_figure, Point):
                paint.paint_point(painter, coo, 6, Qt.cyan)
            elif isinstance(selected_figure, Segment):
                paint.paint_segment(painter, coo, 3, Qt.blue)
            else:
                raise RuntimeError(
                    f'Unexpected figure type {type(selected_figure)}')

        # Finish painting
        painter.restore()
        painter.end()

    def to_real_xy(self, x, y) -> tuple:
        return x - self.center[0], y - self.center[1]

    def handle_mouse_move_event(
            self, event, bindings: List[Binding], figures: Dict[str, Figure],
            allowed_bindings_types: Optional[Tuple[Type, ...]] = None
    ):
        # TODO: Status
        # self._logger.debug('handle_mouse_move_event start')

        # Convert mouse coordinates to drawing space
        x, y = self.to_real_xy(event.x(), event.y())
        self._mouse_xy = (x, y)

        best_bindings = choose_best_bindings(bindings, x, y)
        self._current_bindings = []
        for binding in best_bindings:
            if allowed_bindings_types is None \
                    or isinstance(binding, allowed_bindings_types):
                self._current_bindings.append(binding)
                # self._current_bindings.append(binding)

    def handle_mouse_release_event(self,
                                   bindings,
                                   event,
                                   choose,
                                   controller_work_st):
        pass

