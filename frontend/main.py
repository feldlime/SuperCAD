import sys  # sys нужен для передачи argv в QApplication
from math import sqrt, pow

from PyQt5 import QtWidgets, QtCore

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt, QTimer
from PyQt5.QtGui import (QBrush, QColor, QFont, QLinearGradient, QPainter,
                         QPen, QSurfaceFormat, QCursor)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QOpenGLWidget,
                             QWidget)

import design  # Это наш конвертированный файл дизайна
from figures import *


class Helper(object):
    def __init__(self):
        self.point_end = [0, 0]
        self.point_start = [0, 0]

    def paint(self, painter, event, center_width, center_height, segments_array, points_array, segments_array_view,
              points_array_view, mouse_xy):
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255)))
        # Настраиваем кисть
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.save()
        painter.translate(center_width, center_height)

        # Рисуем координаты рядом с мышкой
        painter.drawText(QPointF(mouse_xy[0] + 15, mouse_xy[1] + 10), str(mouse_xy[0]) + 'x' + str(mouse_xy[1] * (-1)))

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
        for point in points_array_view:
            to_draw = point.get_base_representation()
            painter.drawEllipse(*to_draw, 4, 4)

        painter.restore()


class GLWidget(QOpenGLWidget):
    def __init__(self, helper, parent):
        super(GLWidget, self).__init__(parent.work_plane)

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
            xx = [segment_pos[0], segment_pos[2]] if segment_pos[0] < segment_pos[2] else [segment_pos[2],
                                                                                           segment_pos[0]]
            yy = [segment_pos[1], segment_pos[3]] if segment_pos[1] < segment_pos[3] else [segment_pos[3],
                                                                                           segment_pos[1]]
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
        # Рисование линий
        if event.button() == Qt.LeftButton:
            x = event.x()
            y = event.y()
            self.drag_to_print = True
            self.helper.point_start = [x - self.center_width, y - self.center_height]
            self.helper.point_end = [x - self.center_width + 1, y - self.center_height + 1]
            s = Segment.from_points(self.helper.point_start[0],
                                    self.helper.point_start[1],
                                    self.helper.point_end[0],
                                    self.helper.point_end[1])
            self.segments_array.append(s)

        # Рисование точек
        elif event.button() == Qt.RightButton:
            self.drag_to_print = False
            x = event.x()
            y = event.y()
            p = Point.from_coordinates(x - self.center_width, y - self.center_height)
            self.points_array.append(p)

        # Для не_рисования линни, когда перетягиваем мышь
        else:
            self.drag_to_print = False
            print('else')

    # Отслеживание отпускания клавиши мыши
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_to_print = False


class MainWindow(QtWidgets.QMainWindow, design.Ui_SuperCAD):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super(MainWindow, self).__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Дописываем design под себя
        self.listView.hide()
        self.Point_widget.hide()
        self.Line_widget.hide()
        self.actionShow_elements_table.triggered['bool'].connect(self.triggered_list_view)
        self.point.clicked['bool'].connect(self.triggered_point_widget)
        self.line.clicked['bool'].connect(self.triggered_line_widget)
        self.combine_points.clicked['bool'].connect(self.triggered_combine_points_widget)
        self.point_on_middle_line.clicked['bool'].connect(self.triggered_point_on_middle_line_widget)
        self.point_on_line.clicked['bool'].connect(self.triggered_point_on_line_widget)
        self.parallelism.clicked['bool'].connect(self.triggered_parallelism_widget)
        self.normal.clicked['bool'].connect(self.triggered_normal_widget)
        self.horizontally.clicked['bool'].connect(self.triggered_horizontally_widget)
        self.fix_size.clicked['bool'].connect(self.triggered_fix_size_widget)
        self.fix_point.clicked['bool'].connect(self.triggered_fix_point_widget)
        self.fix_length.clicked['bool'].connect(self.triggered_fix_length_widget)
        self.fix_angle.clicked['bool'].connect(self.triggered_fix_angle_widget)

        helper = Helper()
        openGL = GLWidget(helper, self)

        timer = QTimer(self)
        timer.timeout.connect(openGL.animate)
        timer.start(1)

    def triggered_list_view(self, change):
        if change:
            self.listView.show()
        else:
            self.listView.hide()

    def triggered_point_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Point')
            self.Point_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Point_widget.hide()

    def triggered_line_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Line')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_combine_points_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose first point to combine')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_point_on_middle_line_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose line to combine with middle of line')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_point_on_line_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose line to combine with line')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_parallelism_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose changeable line')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_normal_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose changeable line')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_horizontally_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose changeable line')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_fix_size_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose line for fix size')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_fix_point_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose point for fix')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_fix_length_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose point for fix length')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_fix_angle_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose first line for fix angle')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def hide_all_footer_widgets(self):
        self.Line_widget.hide()
        self.Point_widget.hide()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp

    window.show()  # Показываем окно

    sys.exit(app.exec_())  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
