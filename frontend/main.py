import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt, QTimer
from PyQt5.QtGui import (QBrush, QColor, QFont, QLinearGradient, QPainter,
                         QPen, QSurfaceFormat)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QOpenGLWidget,
                             QWidget)
from time import sleep

import design  # Это наш конвертированный файл дизайна
from figures import *


class Helper(object):
    def __init__(self):
        self.point_end = [0, 0]
        self.point_start = [0, 0]

    def paint(self, painter, event, center_width, center_height, s):
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255)))
        painter.save()
        painter.translate(center_width, center_height)
        for line in s:
            to_draw = line.get_base_representation()
            painter.drawLine(*to_draw)

        # print('paint', len(s))
        painter.restore()


class GLWidget(QOpenGLWidget):
    def __init__(self, helper, parent):
        super(GLWidget, self).__init__(parent.work_plane)

        self.helper = helper
        self.elapsed = 0
        self.setAutoFillBackground(True)

        self.setGeometry(QtCore.QRect(0, 0, parent.work_plane.width(), parent.work_plane.height()))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        self.center_height = parent.work_plane.height() // 2
        self.center_width = parent.work_plane.width() // 2

        self.setSizePolicy(sizePolicy)
        # s1 = Segment()
        self.s = []

    def animate(self):
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.helper.paint(painter, event, self.center_width, self.center_height, self.s)
        painter.end()

    def mouseMoveEvent(self, event):
        if self.drag_to_print:
            x = event.x()
            y = event.y()
            self.helper.point_end = [x - self.center_width, y - self.center_height]
            self.s[-1] = Segment.from_points(self.helper.point_start[0],
                                             self.helper.point_start[1],
                                             self.helper.point_end[0],
                                             self.helper.point_end[1])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x()
            y = event.y()
            self.drag_to_print = True
            self.helper.point_start = [x - self.center_width, y - self.center_height]
            self.helper.point_end = [x - self.center_width + 1, y - self.center_height + 1]
            s1 = Segment.from_points(self.helper.point_start[0],
                                     self.helper.point_start[1],
                                     self.helper.point_end[0],
                                     self.helper.point_end[1])
            self.s.append(s1)
        else:
            self.drag_to_print = False
            print('else')


class MainWindow(QtWidgets.QMainWindow, design.Ui_SuperCAD):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super(MainWindow, self).__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Дописываем design под себя
        self.listView.hide()
        self.actionShow_elements_table.triggered['bool'].connect(self.triggered_list_view)

        helper = Helper()
        openGL = GLWidget(helper, self)

        timer = QTimer(self)
        timer.timeout.connect(openGL.animate)
        timer.start(50)

    def triggered_list_view(self, change):
        if change:
            self.listView.show()
        else:
            self.listView.hide()


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp

    window.show()  # Показываем окно

    sys.exit(app.exec_())  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
