"""Module with main class of application that manage system and picture."""


from glwindow_processing import GLWindowProcessor
from interface import InterfaceProcessor
from project import CADProject, ActionImpossible
from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow

from design import Ui_window
import logging


class Sts:
    NOTHING = 0
    DRAWING_POINT = 1
    DRAWING_SEGMENT = 2
    MOVING_FIGURE = 3

# class FS(Sts):  # Figure statuses


class WindowContent(QOpenGLWidget, Ui_window):
    def __init__(self, window: QMainWindow):
        self._logger = logging.getLogger('WindowContent')

        # Set key private attributes
        self._window = window
        self._project = CADProject()
        self._glwindow_proc = GLWindowProcessor(self)
        self._interface_proc = InterfaceProcessor()

        # Setup basic UI - from design.py
        self.setupUi(self._window)

        # Init GLWidget: self.work_plane - QOpenGLWidget that was created into
        # setupUi in design.py
        super().__init__(self.work_plane)

        # Set additional private attributes
        self._status = Sts.NOTHING
        self._buttons_to_widgets_dict = self._get_buttons_to_widgets_dict()

        # Setup special UI - method _setup_ui
        self._setup_ui()

        # Setup special parameters for glwindow (i.e. for self)
        self._glwindow_proc.setup(
            self.work_plane.width(), self.work_plane.height())

        # Setup handlers (only for ui, because handlers for glwindow are
        # default methods)
        self._setup_handlers()

    def _setup_ui(self):
        self._logger.debug('setup_ui start')

        self.widget_elements_table.hide()
        self._hide_footer_widgets()
        self.action_show_elements_table.triggered['bool'].connect(
            lambda ev: self._interface_proc.trigger_widget(
                self.widget_elements_table, ev))

        # # TODO: Remove unnecessary (duplicate design.py)
        # self._window.setAutoFillBackground(True)
        # self._window.setMouseTracking(True)
        #
        #     # Располагаем виджет в области work_plane и присваеваем ему те же
        #     # паркаметры как в design
        # self._window.setGeometry(QtCore.QRect(
        #     0,
        #     0,
        #     self.work_plane.width(),
        #     self.work_plane.height())
        # )
        #
        # size_policy = QtWidgets.QSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred,
        #     QtWidgets.QSizePolicy.Preferred
        # )
        # size_policy.setHorizontalStretch(0)
        # size_policy.setVerticalStretch(0)
        # size_policy.setHeightForWidth(
        #         self._window.sizePolicy().hasHeightForWidth()
        # )
        # self._window.setSizePolicy(size_policy)

    def _setup_handlers(self):
        pass
        # TODO: Сделать кнопки списком и под каждую написать свою функцию
        # for button_name, widget_name in self._buttons_to_widgets_dict.items():
        #     button = getattr(self, button_name)
        #     widget = getattr(self, widget_name)
        #     print(button, button_name ,widget ,widget_name)
        #     button.clicked['bool'].connect()

    @property
    def _footer_widgets(self) -> dict:
        widgets = dict()
        for w_name in self._buttons_to_widgets_dict.values():
            widgets[w_name] = getattr(self, w_name)
        return widgets

    @property
    def _left_buttons(self) -> dict:
        buttons = dict()
        for b_name in self._buttons_to_widgets_dict.keys():
            buttons[b_name] = getattr(self, b_name)
        return buttons

    def animate(self):
        self.update()

    def paintEvent(self, event):
        # self._logger.debug('paintEvent')
        self._glwindow_proc.paint_all(
            event,
            self._project.figures
        )

    def mouseMoveEvent(self, event):
        self._glwindow_proc.handle_mouse_move_event(
            event,
            self._project.bindings,
            self._project.figures
        )

    def mouseReleaseEvent(self, event):
        self._glwindow_proc.handle_mouse_release_event(event)

    def _trigger_widget(self, button, widget_name, show: bool = False):
        widget = getattr(self, widget_name)
        print(button, widget, widget_name, show)
        self._hide_footer_widgets()
        self._uncheck_left_buttons()
        # self._interf ace_proc.trigger_button(button, show)
        self._interface_proc.trigger_widget(widget, show)

    def _hide_footer_widgets(self):
        for w_name, widget in self._footer_widgets.items():
            self._interface_proc.trigger_widget(widget, False)

    def _uncheck_left_buttons(self):
        for b_name, button in self._left_buttons.items():
            self._interface_proc.trigger_button(button, False)

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

    def _get_buttons_to_widgets_dict(self):
        buttons_to_widgets_dict = dict()
        for name in dir(self):
            if name.startswith('button_'):
                widget_name = 'widget' + name[6:]
                if widget_name in dir(self):
                    buttons_to_widgets_dict[name] = widget_name
        return buttons_to_widgets_dict
