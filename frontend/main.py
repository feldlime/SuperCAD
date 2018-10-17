import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

# import os
# from PyQt5 import uic

import design  # Это наш конвертированный файл дизайна

point_start = [0, 0]
point_end = [30, 30]


class MainWindow(QtWidgets.QMainWindow, design.Ui_SuperCAD):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Использовать двойную буферезацию и цвета в формате RGB (Красный Синий Зеленый)
        glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB)
        glut.glutInit(sys.argv)  # Иницилизируем GL

        self.windowsHeight = self.work_plane.height()
        self.windowsWidth = self.work_plane.width()

        self.work_plane.initializeGL()
        self.work_plane.resizeGL(self.windowsWidth, self.windowsHeight)
        self.work_plane.paintGL = self.paintGL
        self.work_plane.initializeGL = self.initializeGL

        timer = QTimer(self)
        timer.timeout.connect(self.drow)
        timer.start(50)

    def mouseMoveEvent(self, e):
        # self.setupUi(self) # Если это разкоментить, то координаты будут выводиться в статус бар
        x = e.x()
        y = e.y()
        text = "x: {0},  y: {1}".format(x, y)
        global point_end
        point_end = [int(abs(x-self.windowsWidth/2)), int(abs(y-self.windowsHeight/2))]
        # self.statusbar.showMessage(text)  # Если это разкоментить, то координаты будут выводиться в статус бар
        # print(text)

    def paintGL(self):
        self.loadScene()
        glut.glutWireSphere(2, 13, 13)

    def initializeGL(self):
        print("\033[4;30;102m INITIALIZE GL \033[0m")
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def loadScene(self):
        glu.gluLookAt(100, 100, 100, 0, 0, 0, 0, 1, 0)  # Установка камеры
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)  # Установка цвета заливки фона

        gl.glMatrixMode(gl.GL_PROJECTION)  # Установка матрицы проекции
        gl.glLoadIdentity()  # Сброс матрици проекции в единичную
        x, y, width, height = gl.glGetDoublev(gl.GL_VIEWPORT)  # Считываем параметры окна, вроде
        glu.gluPerspective(  # Строим пирамиду охвата видимости
            45,  # field of view in degrees
            width / float(height or 1),  # aspect ratio
            .25,  # near clipping plane
            200,  # far clipping plane
        )

        # gl.glBegin(gl.GL_POINT)
        # for i in range(0, 10):
        #     gl.glVertex2i( 5 * i, 3)
        #
        # gl.glEnd()
        #
        global point_end
        global point_start
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2i(point_start[0], point_start[1])
        gl.glVertex2i(point_end[0], point_start[1])
        gl.glEnd()

        # gl.glMatrixMode(gl.GL_MODELVIEW)

        # gl.glColor3f(1.0, 0.0, 0.0)

        gl.glLoadIdentity()
        gl.glFlush()  # Вывод кадра, после подготовки ( тип вертикальной синхронизации )

        # Определяем процедуру, отвечающую за перерисовку
        # glut.glutDisplayFunc(self.drow())
        # # Определяем процедуру, выполняющуюся при "простое" программы
        # glut.glutIdleFunc(self.drow())
        # glut.glutMainLoop()


    def triggered_list_view(self, change):
        if change:
            self.listView.show()
        else:
            self.listView.hide()

    def drow(self):
        # glu.gluLookAt(100, 100, 100, 0, 0, 0, 0, 1, 0)  # Установка камеры
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)  # Установка цвета заливки фона и очистка буффера

        gl.glMatrixMode(gl.GL_PROJECTION)  # Установка матрицы проекции
        gl.glLoadIdentity()  # Сброс матрици проекции в единичную
        # x, y, width, height = gl.glGetDoublev(gl.GL_VIEWPORT)   # Считываем параметры окна, вроде
        # glu.gluPerspective( # Строим пирамиду охвата видимости
        #     45,  # field of view in degrees
        #     width / float(height or 1),  # aspect ratio
        #     .25,  # near clipping plane
        #     200,  # far clipping plane
        # )

        # gl.glBegin(gl.GL_POINT)
        # for i in range(0, 10):
        #     gl.glVertex2i( 5 * i, 3)
        #
        # gl.glEnd()
        #
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2i(point_start[0], point_start[1])
        gl.glVertex2i(point_end[0], point_start[1])
        gl.glEnd()
        print(point_end)
        # gl.glMatrixMode(gl.GL_MODELVIEW)

        # gl.glColor3f(1.0, 0.0, 0.0)
        gl.glLoadIdentity()
        gl.glFlush()  # Вывод кадра, после подготовки ( тип вертикальной синхронизации )
        # glut.glutSwapBuffers()  # Выводим все нарисованное в памяти на экран
        # print('q')
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.drow()
        painter.end()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp

    window.show()  # Показываем окно

    sys.exit(app.exec_())  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
