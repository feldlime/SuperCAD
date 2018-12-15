"""Module of OpenGL widget"""
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPaintEvent

from logging import getLogger
from typing import Dict, Tuple, List, Optional, Type

import paint

from figures import Figure, Point, Segment
from bindings import (
    Binding,
    choose_best_bindings
)


class GLWindowProcessor:
    def __init__(self, glwindow):
        self._logger = getLogger('GLWindowProcessor')

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

        # Set focus on window for keyPressEvent
        self._glwindow.setFocusPolicy(Qt.StrongFocus)

    @property
    def center(self) -> tuple:
        return self._glwindow.width() // 2, self._glwindow.height() // 2

    def paint_all(self, event: QPaintEvent,
                  mouse_xy,
                  bindings,
                  figures: Dict[str, Figure],
                  selected_figures: list,
                  painted_figure: Optional[Figure] = None,
                  ):
        # self._logger.debug('paint_all start')
        painter = QPainter()
        painter.begin(self._glwindow)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255)))
        painter.save()
        painter.translate(*self.center)

        # self._logger.debug(f'current_bindings: {self._current_bindings}')
        paint.paint_all(
            painter, figures, bindings, mouse_xy
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
        for selected_figure in selected_figures:
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
        return x - self.center[0], -(y - self.center[1])



