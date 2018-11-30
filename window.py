"""Module with main class of application that manage system and picture."""


from contracts import contract, new_contract
from glwindow_processing import GLWindowProcessor
from interface import InterfaceProcessor
from project import CADProject, ActionImpossible
from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow
import logging

from design import Ui_window
from figures import Figure, Point, Segment
from states import ControllerWorkSt, ChooseSt, ControllerSt
from restrictions import *

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
        # self._status = Sts.NOTHING
        self._buttons_to_widgets_dict = self._get_buttons_to_widgets_dict()

        # Setup special UI - method _setup_ui
        self._setup_ui()

        # Setup special parameters for glwindow (i.e. for self)
        self._glwindow_proc.setup(
            self.work_plane.width(), self.work_plane.height())

        # Setup handlers (only for ui, because handlers for glwindow are
        # default methods)
        self._setup_handlers()

        self.controller_work_st = ControllerWorkSt.NOTHING
        self.choose = ChooseSt.NOTHING
        self.choose_len = 0
        self.choose_figures_names = []

    def _setup_ui(self):
        self._logger.debug('setup_ui start')

        self.widget_elements_table.hide()
        self._hide_footer_widgets()
        self.action_show_elements_table.triggered['bool'].connect(
            lambda ev: self._interface_proc.trigger_widget(
                self.widget_elements_table, ev))

    def _setup_handlers(self):
        self.button_add_point.clicked['bool'].connect(
            self.controller_add_point
        )
        self.button_add_segment.clicked['bool'].connect(
            self.controller_add_segment
        )
        self.button_restr_point_fixed.clicked['bool'].connect(
            self.controller_restr_point_fixed
        )
        self.button_restr_point_on_segment.clicked['bool'].connect(
            self.controller_restr_point_on_segment
        )
        self.button_restr_points_joint.clicked['bool'].connect(
            self.controller_restr_point_joint
        )
        self.button_restr_segment_angle_fixed.clicked['bool'].connect(
            self.controller_restr_segment_angle_fixed
        )
        self.button_restr_segment_horizontal.clicked['bool'].connect(
            self.controller_restr_segment_horizontal
        )
        self.button_restr_segment_length_fixed.clicked['bool'].connect(
            self.controller_restr_segment_length_fixed
        )
        self.button_restr_segments_normal.clicked['bool'].connect(
            self.controller_restr_segments_normal
        )
        self.button_restr_segments_parallel.clicked['bool'].connect(
            self.controller_restr_segments_parallel
        )
        self.point_submit.clicked['bool'].connect(
            lambda ev: self.controller_add_point(ControllerSt.SUBMIT)
        )
        self.line_submit.clicked['bool'].connect(
            lambda ev: self.controller_add_segment(ControllerSt.SUBMIT)
        )

    # @contract(status='int', returns='tuple')
    def controller_restr_segments_parallel(self, status: int) -> \
            tuple:
        if status == ControllerSt.HIDE:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
        if status == ControllerSt.SHOW:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
            self.widget_restr_segments_parallel.show()
        if status == ControllerSt.SUBMIT:
            if self.restr_segments_parallel_line_1.checkState() == False or \
                    self.restr_segments_parallel_line_2.checkState() == False:
                raise ValueError
            else:
                pass
            # TODO Вернуть две линии
            # return((self.point_x.value(), self.point_y.value()))

    def controller_show_hide(self, widget, controller_st, controller_work_st):
        self._hide_footer_widgets()
        self._uncheck_left_buttons()
        if controller_st == ControllerSt.HIDE:
            self.controller_work_st = ControllerWorkSt.NOTHING
            self.choose = ChooseSt.NOTHING
            self.choose_figures_names = []
        if controller_st == ControllerSt.SHOW:
            widget.show()
            self.controller_work_st = controller_work_st
            self.choose = ChooseSt.CHOOSE

    def controller_restr_segments_normal(self, status, figure: str=None):
        if status == ControllerSt.SUBMIT:
            if not self.restr_segments_normal_line_1.checkState() or \
                    not self.restr_segments_normal_line_2.checkState():
                self.choose_figures_names.append(figure)
            else:
                restr = SegmentsParallel()
                self.controller_work_st = ControllerWorkSt.NOTHING
                self.choose = ChooseSt.NOTHING
                self.choose_figures_names = []
        else:
            self.controller_show_hide(self.widget_restr_segments_normal,
                                      status,
                                      ControllerWorkSt.RESTR_SEGMENTS_NORMAL)


    def controller_restr_segment_length_fixed(self, status):
        if status == ControllerSt.SUBMIT:
            if not self.restr_segment_length_fixed_line.checkState():
                pass
            else:
                pass
        else:
            self.controller_show_hide(self.widget_restr_segment_length_fixed,
                                      status,
                                      ControllerWorkSt.
                                      RESTR_SEGMENT_LENGTH_FIXED)

    def controller_restr_segment_horizontal(self, status):
        if status == ControllerSt.SUBMIT:
            if not self.restr_segment_horizontal_line.checkState():
                pass
            else:
                pass
        else:
            self.controller_show_hide(self.widget_restr_segment_horizontal,
                                      status,
                                      ControllerWorkSt.RESTR_SEGMENT_HORIZONTAL)

    def controller_restr_segment_angle_fixed(self, status):
        if status == ControllerSt.SUBMIT:
            if not self.restr_segment_angle_fixed_line_1.checkState() or not\
                    self.restr_segment_angle_fixed_line_2.checkState():
                pass
            else:
                pass
        else:
            self.controller_show_hide(self.widget_restr_segment_angle_fixed,
                                      status,
                                      ControllerWorkSt.
                                      RESTR_SEGMENT_ANGLE_FIXED)

    def controller_restr_point_joint(self, status, figure: str=None):
        if status == ControllerSt.SUBMIT:
            if not self.restr_points_joint_point_1.checkState() or \
                    not self.restr_points_joint_point_2.checkState():
                self.choose_figures_names.append(figure)
            else:
                # restr = SegmentsSpotsJoint(,)
                self.controller_work_st = ControllerWorkSt.NOTHING
                self.choose = ChooseSt.NOTHING
                self.choose_figures_names = []
        else:
            self.controller_show_hide(self.widget_restr_points_joint,
                                      status,
                                      ControllerWorkSt.RESTR_POINTS_JOINT)

    # @contract(status='int', returns='tuple')
    def controller_restr_point_on_segment(self, status, figure: str=None):
        if status == ControllerSt.SUBMIT:
            if self.restr_point_on_segment_line.checkState() == False or \
                    self.restr_point_on_segment_point.checkState() == False:
                raise ValueError
            else:
                pass
        else:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
            if status == ControllerSt.SHOW:
                self.widget_restr_point_on_segment.show()

    # @contract(status='int')
    def controller_restr_point_fixed(self, status, figure: str=None):
        if status == ControllerSt.SUBMIT:
            if not self.restr_point_fixed_point.checkState():
                pass
            else:
                pass
        else:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
            if status == ControllerSt.SHOW:
                self.widget_restr_point_fixed.show()


    def controller_add_segment(self, status):
        self._logger.debug('controller_add_segment start status ' + str(status))
        if status == ControllerSt.HIDE:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
        if status == ControllerSt.SHOW:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
            self.widget_add_segment.show()
        if status == ControllerSt.SUBMIT:
            if float(self.line_x_1.value()) ==\
                float(self.line_x_2.value()) ==\
                float(self.line_y_1.value()) ==\
                float(self.line_y_2.value()):
                raise ValueError
            else:
                s = Segment.from_coordinates(
                    self.line_x_1.value(),
                    self.line_y_1.value(),
                    self.line_x_2.value(),
                    self.line_y_2.value())
                self._project.add_figure(s)

    def controller_add_point(self, status):
        self._logger.debug('controller_add_point start wits status' + str(
            status))
        if status == ControllerSt.HIDE:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
        if status == ControllerSt.SHOW:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
            self.widget_add_point.show()
        if status == ControllerSt.SUBMIT:
            x = self.point_x.value()
            y = self.point_y.value()
            self._project.add_figure(Point((x, y)))

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
        self._glwindow_proc.handle_mouse_release_event(event,
                                                       self._project.bindings,
                                                       self.choose,
                                                       self.controller_work_st)

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
