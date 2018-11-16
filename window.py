"""Module with main class of application that manage system and picture."""
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

from glwindow_processing import GLWindowProcessor
from interface import InterfaceProcessor
from project import CADProject, ActionImpossible
from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from design import Ui_window


class Sts:
    NOTHING = 0
    DRAWING_POINT = 1
    DRAWING_SEGMENT = 2
    MOVING_FIGURE = 3

class FS(Sts):  # Figure statuses

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
        self._glwindow_proc = GLWindowProcessor(window.work_plane)
        self._interface_proc = InterfaceProcessor()

        self._status = Sts.NOTHING

        self._last_clicked_point = (0, 0)  # x, y

        self._highlighted_figures_names = []

        self._buttons_to_widgets_dict = dict()
        for name in dir(self):
            if name.startswith('button_'):
                widget_name = 'widget' + name[6:]
                if widget_name in dir(self):
                    self._buttons_to_widgets_dict[name] = widget_name

        self._setup_ui()
        self._setup_handlers()

    def _setup_ui(self):
        self.setupUi(self._window)

        self.center = (
                self._window.work_plane.height() // 2,
                self._window.work_plane.height() // 2
        )

        self.widget_list_objects.hide()
        self.hide_all_footer_widgets()
        self.action_show_elements_table.triggered['bool'].connect(
            self._interface_proc._trigger_)

        # TODO: Remove unnecessary (duplicate design.py)
        self._window.setAutoFillBackground(True)
        self._window.setMouseTracking(True)

            # Располагаем виджет в области work_plane и присваеваем ему те же
            # паркаметры как в design
        self._window.setGeometry(QtCore.QRect(
            0,
            0,
            self._window.work_plane.width(),
            self._window.work_plane.height())
        )

        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
                self._window.sizePolicy().hasHeightForWidth()
        )
        self._window.setSizePolicy(size_policy)

    def _setup_handlers(self):
        for button_name, widget_name in self._buttons_to_widgets_dict.items():
            button = getattr(self, button_name)
            widget = getattr(self, widget_name)
            button.clicked['bool'].connect(self._trigger_widget(widget))

    @property
    def _footer_widgets(self):
        return list(self._buttons_to_widgets_dict.values())

    @property
    def _left_buttons(self):
        return list(self._buttons_to_widgets_dict.keys())

    def mouse_xy(self, event):
        return event.x() - self.center[0], event.y() - self.center[1]

    def _trigger_widget(self, widget, show: bool = False):
        self._hide_footer_widgets()
        self._uncheck_left_buttons()
        self._interface_proc.trigger_widget(widget, show)

    def _hide_footer_widgets(self):
        for widget in self._footer_widgets:
            self._interface_proc.trigger_widget(widget, False)

    def _uncheck_left_buttons(self):
        for button in self._left_buttons:
            self._interface_proc.trigger_button(button, False)

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

    def _save(self):
        # TODO: window for saving, event -> get filename
        filename = ''
        self._project.save(filename)

    def _load(self):
        # TODO: window for loading, event -> get filename
        filename = ''
        self._project.load(filename)

    def _undo(self):
        try:
            self._project.undo()
        except ActionImpossible:
            # TODO: Status bar / inactive
            pass

    def _redo(self):
        try:
            self._project.redo()
        except ActionImpossible:
            # TODO: Status bar / inactive
            pass
