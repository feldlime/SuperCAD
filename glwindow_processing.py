"""Module of OpenGL widget"""
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPaintEvent

import logging
from typing import Dict, Tuple, List

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
                  ferst_line_coo):
        self._logger.debug('paint_all start')
        painter = QPainter()
        painter.begin(self._glwindow)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255)))
        painter.save()
        painter.translate(*self.center)

        paint.paint_all(
            painter, figures, self._current_bindings, self._mouse_xy,
            self.center, event.rect()
        )
        if len(ferst_line_coo) == 2:
            paint.paint_line(
                painter, ferst_line_coo, self._mouse_xy
            )
        painter.restore()
        painter.end()

    def to_real_xy(self, x, y) -> tuple:
        return x - self.center[0], y - self.center[1]

    def handle_mouse_move_event(
            self, event, bindings: List[Binding], figures: Dict[str, Figure]):
        # TODO: Status
        self._logger.debug('handle_mouse_move_event start')

        # Convert mouse coordinates to drawing space
        x, y = self.to_real_xy(event.x(), event.y())
        self._mouse_xy = (x, y)

        self._logger.debug(f'bindings: {bindings}')
        self._highlighted_figures_names = []


        best_bindings = choose_best_bindings(bindings, x, y)
        for bind in best_bindings:
            if ControllerWorkSt.RESTR_JOINT:
                if isinstance(bind, (SegmentEndBinding,
                                     SegmentStartBinding,
                                     SegmentCenterBinding)):
            #         TODO: Подсветить+
                    pass



            for name in bind.get_object_names():
                self._highlighted_figures_names.append(name)

    def handle_mouse_release_event(self,
                                   bindings,
                                   event,
                                   choose,
                                   controller_work_st):
        pass

