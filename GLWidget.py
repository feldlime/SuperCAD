from math import sqrt, pow

from PyQt5 import QtWidgets, QtCore

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QOpenGLWidget


class GLWidget(QOpenGLWidget):
    def __init__(self, helper, parent):
        super(GLWidget, self).__init__(parent.work_plane)

        self.parent = parent
        self.helper = helper

        self.elapsed = 0
        self.setAutoFillBackground(True)
        self.setMouseTracking(True)

        # Располагаем виджет в области work_plane и присваеваем ему те же паркаметры как в design
        self.setGeometry(QtCore.QRect(0, 0, parent.work_plane.width(), parent.work_plane.height()))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        # Вычисляем центр поля
        self.center_height = parent.work_plane.height() // 2
        self.center_width = parent.work_plane.width() // 2

        self.setSizePolicy(sizePolicy)

        # Для рисования линнии, что бы знать, когда рисование окончено, можно так же найти как отслеживать отпускание
        # левой кнопки мыши, но я не нашел
        self.drag_to_print = False
        # Массив линий и точек
        self.segments_array = []
        self.points_array = []
        # Массивы выделенных линий и точек
        self.segments_array_view = []
        self.points_array_view = []

        self.mouse_xy = [0, 0]

    def animate(self):
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.helper.paint(painter, event, self.center_width, self.center_height, self.segments_array, self.points_array,
                          self.segments_array_view, self.points_array_view, self.mouse_xy)
        painter.end()

    # Отслеживание передвижения мыши
    def mouseMoveEvent(self, event):
        # На каком расстоянии от мышки, объект будет выделяться
        near_size = 8

        # Переводим координаты от мышки, в координаты пространства
        self.mouse_xy[0] = x = event.x() - self.center_width
        self.mouse_xy[1] = y = event.y() - self.center_height

        # Обнуляем массивы с выделеными объектам
        self.segments_array_view = []
        self.points_array_view = []

        # Дэтектим мышку рядом с точкой
        for point in self.points_array:
            point_pos = point.get_base_representation()
            if abs(x - point_pos[0]) < near_size and abs(y - point_pos[1]) < near_size:
                self.points_array_view.append(point)

        # Детектим мышку рядом с сегментом
        for segment in self.segments_array:
            segment_pos = segment.get_base_representation()
            xx = [segment_pos[0], segment_pos[2]] \
                if segment_pos[0] < segment_pos[2] \
                else [segment_pos[2], segment_pos[0]]
            yy = [segment_pos[1], segment_pos[3]] \
                if segment_pos[1] < segment_pos[3] \
                else [segment_pos[3], segment_pos[1]]
            # Проверяем, находиться ли мышка в квадрате сегмента
            if x <= xx[1] and x >= xx[0] and y <= yy[1] and y >= yy[0]:
                # Длинное уравнение нахождения расстояния от точки до прямой
                d = ((segment_pos[1] - segment_pos[3]) * x + (segment_pos[2] - segment_pos[0]) * y + (
                        segment_pos[0] * segment_pos[3] - segment_pos[2] * segment_pos[1])) / sqrt(
                    pow(segment_pos[2] - segment_pos[0], 2) + pow(segment_pos[3] - segment_pos[1], 2))
                if abs(d) - near_size < 0:
                    self.segments_array_view.append(segment)

        # Это для отслеживания передвижения мышки, когда рисуем линию и нажата левая
        if self.drag_to_print:
            self.helper.point_end = [x, y]
            s = Segment.from_points(self.helper.point_start[0],
                                    self.helper.point_start[1],
                                    self.helper.point_end[0],
                                    self.helper.point_end[1])
            self.segments_array[-1] = s
            self.segments_array_view.append(s)

    # Отслеживание нажатия клавиши мыши
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Рисование линий
            if not self.parent.Line_widget.isHidden():
                x = event.x()
                y = event.y()
                self.drag_to_print = True
                self.helper.point_start = [x - self.center_width,
                                           y - self.center_height]
                self.helper.point_end = [x - self.center_width + 1,
                                         y - self.center_height + 1]
                s = Segment.from_points(self.helper.point_start[0],
                                        self.helper.point_start[1],
                                        self.helper.point_end[0],
                                        self.helper.point_end[1])
                self.segments_array.append(s)

            # Рисование точек
            elif not self.parent.Point_widget.isHidden():
                self.drag_to_print = False
                x = event.x()
                y = event.y()
                p = Point.from_coordinates(x - self.center_width,
                                           y - self.center_height)
                self.points_array.append(p)

            # Для не_рисования линни, когда перетягиваем мышь
            else:
                self.drag_to_print = False
                print('else')

    # Отслеживание отпускания клавиши мыши
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_to_print = False