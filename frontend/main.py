import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt, QTimer
from PyQt5.QtGui import (QBrush, QColor, QFont, QLinearGradient, QPainter,
                         QPen, QSurfaceFormat)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QOpenGLWidget,
                             QWidget)

# import os
# from PyQt5 import uic

import design  # Это наш конвертированный файл дизайна


class Helper(object):
    def __init__(self):
        self.point_end = [0, 0]
        self.point_start = [0, 0]

    def paint(self, painter, event, elapsed):
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255)))
        painter.save()
        painter.drawLine(self.point_start[0], self.point_start[1], self.point_end[0], self.point_end[1])
        painter.restore()


class GLWidget(QOpenGLWidget):
    def __init__(self, helper, parent):
        super(GLWidget, self).__init__(parent.work_plane)

        self.helper = helper
        self.elapsed = 0
        # self.setFixedSize(200, 200)
        self.setAutoFillBackground(True)
        #
        self.setGeometry(QtCore.QRect(0, 0, 1231, 611))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        self.setSizePolicy(sizePolicy)

    def animate(self):
        self.elapsed = (self.elapsed + self.sender().interval()) % 1000
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.helper.paint(painter, event, self.elapsed)
        painter.end()

    def mouseMoveEvent(self, e):
        x = e.x()
        y = e.y()
        self.helper.point_end = [x, y]


class MainWindow(QtWidgets.QMainWindow, design.Ui_SuperCAD):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super(MainWindow, self).__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        helper = Helper()
        openGL = GLWidget(helper, self)


        # layout = QGridLayout()
        # layout.addWidget(openGL, 0, 1)
        # self.setLayout(layout)

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
