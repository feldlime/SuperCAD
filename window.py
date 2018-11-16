"""Module with main class of application that manage system and picture."""
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

from glwidget import GLWidget
from design_functionality import DesignFunctionality
from project import CADProject
from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from design import Ui_window


class MainWindow(QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()

        self._content = WindowContent(self)

        timer = QTimer(self)
        timer.timeout.connect(self._content.animate)
        timer.start(1)


class WindowContent(QOpenGLWidget, Ui_window):
    def __init__(self, window: QMainWindow):
        super().__init__()

        self._window = window
        self._project = CADProject()
        self._glwindow = GLWidget(window)
        self._interface = DesignFunctionality(window)

        # # Массив линий и точек
        # self._window.segments_array = []
        # self._window.points_array = []
        #
        # # Массивы выделенных линий и точек
        # self._window.segments_array_view = []
        # self._window.points_array_view = []
        #
        # self._window.mouse_xy = [0, 0]
        #
        # # If now drawing smt, has coordinats of pooints
        # self._window.now_drawing = []

        self._buttons_to_widgets_dict = dict()
        for name in dir(self):
            if name.startswith('button_'):
                widget_name = 'widget' + name[6:]
                if widget_name in dir(self):
                    self._buttons_to_widgets_dict[name] = widget_name

        self._setup_ui()
        self._setup_handlers()


        self.actionShow_elements_table.triggered['bool'].connect(
            self.triggered_list_view)
        self.point.clicked['bool'].connect(
            self.triggered_widget("Point_widget"))
        self.line.clicked['bool'].connect(
            self.triggered_widget("Line_widget"))
        self.combine_points.clicked['bool'].connect(
            self.triggered_widget("Combine_points_widget"))
        self.point_on_middle_line.clicked['bool'].connect(
            self.triggered_widget("Point_on_middle_line_widget"))
        self.point_on_line.clicked['bool'].connect(
            self.triggered_widget("Point_on_line_widget"))
        self.parallelism.clicked['bool'].connect(
            self.triggered_widget("Parallelism_widget"))
        self.normal.clicked['bool'].connect(
            self.triggered_widget("Normal_widget"))
        self.horizontally.clicked['bool'].connect(
            self.triggered_widget("Horizontally_widget"))
        self.fix_size.clicked['bool'].connect(
            self.triggered_widget("Fix_size_widget"))
        self.fix_point.clicked['bool'].connect(
            self.triggered_widget("Fix_point_widget"))
        self.fix_length.clicked['bool'].connect(
            self.triggered_widget("Fix_length_widget"))
        self.fix_angle.clicked['bool'].connect(
            self.triggered_widget("Fix_angle_widget"))

        self._design.setup_ui(window=self)  # design init

        self.painter = QPainter()

    def _setup_ui(self):
        self.setupUi(self._window)
        self.listView.hide()
        self.hide_all_footer_widgets()

    def animate(self):
        self.update()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.Antialiasing)
        self.painter.paint(self.painter,
                           event,
                           self.center_width,
                           self.center_height,
                           self.segments_array,
                           self.points_array,
                           self.segments_array_view,
                           self.points_array_view,
                           self.mouse_xy)
        self.painter.end()

    # Отслеживание передвижения мыши
    def mouseMoveEvent(self, event):
        # На каком расстоянии от мышки, объект будет выделяться
        near_size = 8

        # Convert mouse coordinats to drawing space
        self.mouse_xy[0] = x = event.x() - self.center_width
        self.mouse_xy[1] = y = event.y() - self.center_height

        self.points_array_view = self.points_array
        self.segments_array_view = self.segments_array

        # TODO: Для полчучения привязок
        # project.get_bindings -> bindings.get_best_bindings
        # TODO: Для подсветки анализируем класс привязки и вызываем
        # bindings.object.bind
        # TODO: Для получения фигуры
        # bindinsg.object.get_object_names -> список имен объектов
        # project.get_figure(object_name) -> object_figure

        if not self.window.Line_widget.isHidden():
            if len(self.now_drawing) > 0:
                s = Segment.from_points(self.now_drawing[0][0],
                                        self.now_drawing[0][1],
                                        x,
                                        y)
                self.segments_array_view.append(s)
            else:
                p = Point.from_coordinates(x, y)
                self.points_array_view.append(p)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            x, y = self.mouse_xy
            self.now_drawing.append([x, y])

            if not self._window.Point_widget.isHidden():
                p = Point.from_coordinates(x, y)
                self.points_array.append(p)
                self.now_drawing = []

            if not self._window.Line_widget.isHidden() and len(
                    self.now_drawing) > 0:
                s = Segment.from_points(self.now_drawing[0][0],
                                        self.now_drawing[0][1],
                                        self.now_drawing[1][0],
                                        self.now_drawing[1][1])
                self.segments_array.append(s)
                self.now_drawing = []
    # def animate(self):
    #     self.update()
    # #                                     self.now_drawing[1][1])
    #             self.segments_array.append(s)
    #             self.now_drawing = []

