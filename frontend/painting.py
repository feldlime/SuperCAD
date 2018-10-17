#!/usr/bin/env python

import sys

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt, QTimer
from PyQt5.QtGui import (QBrush, QColor, QFont, QLinearGradient, QPainter,
                         QPen, QSurfaceFormat)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QOpenGLWidget,
                             QWidget)


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
        super(GLWidget, self).__init__(parent)

        self.helper = helper
        self.elapsed = 0
        self.setFixedSize(200, 200)
        self.setAutoFillBackground(False)

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


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle("2D Painting on Native and OpenGL Widgets")

        helper = Helper()
        openGL = GLWidget(helper, self)
        openGLLabel = QLabel("OpenGL")
        openGLLabel.setAlignment(Qt.AlignHCenter)

        layout = QGridLayout()
        layout.addWidget(openGL, 0, 1)
        layout.addWidget(openGLLabel, 1, 1)
        self.setLayout(layout)

        timer = QTimer(self)
        timer.timeout.connect(openGL.animate)
        timer.start(50)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fmt = QSurfaceFormat()
    fmt.setSamples(9)
    QSurfaceFormat.setDefaultFormat(fmt)

    window = Window()
    window.show()
    sys.exit(app.exec_())
