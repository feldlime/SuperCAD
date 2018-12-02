"""Module with main class of application that manage system and picture."""


from contracts import contract, new_contract
from glwindow_processing import GLWindowProcessor
from interface import InterfaceProcessor
from project import CADProject, ActionImpossible
from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt
import logging

from design import Ui_window
from figures import Figure, Point, Segment
from states import ControllerWorkSt, ChooseSt, ControllerSt, CreationSt
from restrictions import *
from bindings import (
    Binding,
    PointBinding,
    SegmentStartBinding,
    SegmentCenterBinding,
    SegmentEndBinding,
    SegmentsIntersectionBinding,
    FullSegmentBinding,
    choose_best_bindings
)
from solve import CannotSolveSystemError


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
        self.choosed_bindings = []

        self.painted_figure = None  # Figure that is painted at this moment
        self.creation_st = CreationSt.NOTHING

        self._filename = None

    def _setup_ui(self):
        self._logger.debug('setup_ui start')

        self.widget_elements_table.hide()
        self._hide_footer_widgets()
        self.action_show_elements_table.triggered['bool'].connect(
            lambda ev: self._interface_proc.trigger_widget(
                self.widget_elements_table, ev))

        # Setting tab order. Can do it into designer and remove from here

        # Add point
        self.setTabOrder(self.field_x_add_point, self.field_y_add_point)
        self.setTabOrder(self.field_y_add_point, self.submit_add_point)

        # Add segment
        self.setTabOrder(self.field_x1_add_segment, self.field_y1_add_segment)
        self.setTabOrder(self.field_y1_add_segment, self.field_x2_add_segment)
        self.setTabOrder(self.field_x2_add_segment, self.field_y2_add_segment)
        self.setTabOrder(self.field_y2_add_segment, self.submit_add_segment)

    def _setup_handlers(self):

        # Left buttons
        self.button_add_point.clicked['bool'].connect(
            lambda ev: self.controller_add_point(ControllerSt.SHOW)
        )
        self.button_add_segment.clicked['bool'].connect(
            lambda ev: self.controller_add_segment(ControllerSt.SHOW)
        )
        self.button_restr_fixed.clicked['bool'].connect(
            self.controller_restr_fixed
        )
        self.button_restr_point_on_segment.clicked['bool'].connect(
            self.controller_restr_point_on_segment
        )
        self.button_restr_joint.clicked['bool'].connect(
            self.controller_restr_joint
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

        # Submits
        self.submit_add_point.clicked['bool'].connect(
            lambda ev: self.controller_add_point(ControllerSt.SUBMIT)
        )
        self.submit_add_segment.clicked['bool'].connect(
            lambda ev: self.controller_add_segment(ControllerSt.SUBMIT)
        )
        self.submit_restr_fixed.clicked['bool'].connect(
            lambda ev: self.controller_restr_fixed(ControllerSt.SUBMIT)
        )
        self.submit_restr_joint.clicked['bool'].connect(
            lambda ev: self.controller_restr_joint(ControllerSt.SUBMIT)
        )

        # Fields
        self.field_x_add_point.valueChanged.connect(
            lambda new_value: self.change_painted_figure('x', new_value)
        )
        self.field_y_add_point.valueChanged.connect(
            lambda new_value: self.change_painted_figure('y', new_value)
        )
        self.field_x1_add_segment.valueChanged.connect(
            lambda new_value: self.change_painted_figure('x1', new_value)
        )
        self.field_y1_add_segment.valueChanged.connect(
            lambda new_value: self.change_painted_figure('y1', new_value)
        )
        self.field_x2_add_segment.valueChanged.connect(
            lambda new_value: self.change_painted_figure('x2', new_value)
        )
        self.field_y2_add_segment.valueChanged.connect(
            lambda new_value: self.change_painted_figure('y2', new_value)
        )

        # Actions
        self.action_undo.triggered['bool'].connect(self.undo)
        self.action_redo.triggered['bool'].connect(self.redo)
        self.action_save.triggered['bool'].connect(self.save)
        self.action_save_as.triggered['bool'].connect(self.save_as)
        self.action_open.triggered['bool'].connect(self.open)
        self.action_reset.triggered['bool'].connect(self.reset)
        self.action_new.triggered['bool'].connect(self.new)
        self.action_exit.triggered['bool'].connect(self.exit)

    def change_painted_figure(self, field: str, value: float):
        if self.painted_figure is not None:
            self.painted_figure.set_param(field, value)
        # TODO: Move mouse

    def controller_show_hide(self, widget, controller_st, controller_work_st):
        self._hide_footer_widgets()
        self._uncheck_left_buttons()
        if controller_st == ControllerSt.HIDE:
            self.controller_work_st = ControllerWorkSt.NOTHING
            self.choose = ChooseSt.NOTHING
            self.choosed_bindings = []
            self.painted_figure = None
        if controller_st == ControllerSt.SHOW:
            widget.show()
            self.controller_work_st = controller_work_st
            self.choose = ChooseSt.CHOOSE
        self._logger.debug('End of controller_show_hide')

    def controller_restr_segments_parallel(self, status: int):
        if status == ControllerSt.HIDE:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
        if status == ControllerSt.SHOW:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
            self.widget_restr_segments_parallel.show()
        if status == ControllerSt.SUBMIT:
            if self.checkbox_restr_segments_parallel_1.checkState() == False or \
                    self.checkbox_restr_segments_parallel_2.checkState() == False:
                raise ValueError
            else:
                pass

    def controller_restr_segments_normal(self, status, figure: str=None):
        if status == ControllerSt.SUBMIT:
            if not self.checkbox_restr_segments_normal_1.checkState() or \
                    not self.checkbox_restr_segments_normal_2.checkState():
                self.choosed_bindings.append(figure)
            else:
                restr = SegmentsParallel()
                self.controller_work_st = ControllerWorkSt.NOTHING
                self.choose = ChooseSt.NOTHING
                self.choosed_bindings = []
        else:
            self.controller_show_hide(self.widget_restr_segments_normal,
                                      status,
                                      ControllerWorkSt.RESTR_SEGMENTS_NORMAL)

    def controller_restr_segment_length_fixed(self, status):
        if status == ControllerSt.SUBMIT:
            if not self.checkbox_restr_segment_length_fixed.checkState():
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
            if not self.checkbox_restr_segment_horizontal.checkState():
                pass
            else:
                pass
        else:
            self.controller_show_hide(self.widget_restr_segment_horizontal,
                                      status,
                                      ControllerWorkSt.RESTR_SEGMENT_HORIZONTAL)

    def controller_restr_segment_angle_fixed(self, status):
        if status == ControllerSt.SUBMIT:
            if not self.checkbox_restr_segment_angle_fixed_1.checkState() or not\
                    self.checkbox_restr_segment_angle_fixed_2.checkState():
                pass
            else:
                pass
        else:
            self.controller_show_hide(self.widget_restr_segment_angle_fixed,
                                      status,
                                      ControllerWorkSt.
                                      RESTR_SEGMENT_ANGLE_FIXED)

    def controller_restr_joint(self, status, bindings: list = None):
        if status == ControllerSt.ADD:
            for binding in bindings:
                if isinstance(binding, (PointBinding,
                                        SegmentStartBinding,
                                        SegmentCenterBinding,
                                        SegmentEndBinding)):
                    self.choosed_bindings.append(binding)
                    if len(self.choosed_bindings) == 1:
                        self.checkbox_restr_joint_1.toggle()
                    if len(self.choosed_bindings) == 2:
                        self.checkbox_restr_joint_2.toggle()
                        self.choose = ChooseSt.NOTHING
                    break
        elif status == ControllerSt.SUBMIT:
            if len(self.choosed_bindings) < 2:
                raise RuntimeError

            b1, b2 = self.choosed_bindings
            if isinstance(b1, PointBinding):
                if isinstance(b2, PointBinding):
                    restr = PointsJoint()
                else:
                    spot_type = self.get_spot_type(b2)
                    restr = PointAndSegmentSpotJoint(spot_type)
            else:
                spot_type_1 = self.get_spot_type(b1)
                if isinstance(b2, PointBinding):
                    b1, b2 = b2, b1
                    restr = PointAndSegmentSpotJoint(spot_type_1)
                else:
                    spot_type_2 = self.get_spot_type(b2)
                    restr = SegmentsSpotsJoint(spot_type_1, spot_type_2)
            try:
                self._project.add_restriction(restr,
                                              (b1.get_object_names()[0],
                                               b2.get_object_names()[0]))
            except CannotSolveSystemError:
                pass
            self.controller_work_st = ControllerWorkSt.NOTHING
            self.choosed_bindings = []
            status = ControllerSt.HIDE
        if status == ControllerSt.HIDE or status == ControllerSt.SHOW:
            self.controller_show_hide(self.widget_restr_joint,
                                      status,
                                      ControllerWorkSt.RESTR_JOINT)

    def controller_restr_point_on_segment(self, status, figure: str=None):
        if status == ControllerSt.SUBMIT:
            if not self.checkbox_restr_point_on_segment_line.checkState() or \
                    not self.checkbox_restr_point_on_segment_point.checkState():
                raise ValueError
            else:
                pass
        else:
            pass

    def controller_restr_fixed(self, status, bindings: list = None):
        if status == ControllerSt.ADD:
            for binding in bindings:
                if isinstance(binding, (PointBinding,
                                        SegmentStartBinding,
                                        SegmentCenterBinding,
                                        SegmentEndBinding,
                                        FullSegmentBinding)):
                    self.choosed_bindings.append(binding)
                    if len(self.choosed_bindings) == 1:
                        self.checkbox_restr_fixed.toggle()
                        self.choose = ChooseSt.NOTHING
                    break
        elif status == ControllerSt.SUBMIT:
            if len(self.choosed_bindings) != 1:
                raise RuntimeError
            binding = self.choosed_bindings[0]
            figure_name = binding.get_object_names()[0]
            if isinstance(binding, PointBinding):
                restr = PointFixed(*self._project.figures[
                                       figure_name].get_base_representation())
            elif isinstance(binding, FullSegmentBinding):
                restr = SegmentFixed(*self._project.figures[
                                       figure_name].get_base_representation())
            else:
                binding_spot_type = self.get_spot_type(binding)
                restr = SegmentSpotFixed(*self._project.figures[
                    figure_name].get_base_representation(), binding_spot_type)
            try:
                self._project.add_restriction(restr, tuple([figure_name]))
            except CannotSolveSystemError:
                pass
            self.controller_work_st = ControllerWorkSt.NOTHING
            self.choosed_bindings = []
            status = ControllerSt.HIDE

        if status == ControllerSt.HIDE or status == ControllerSt.SHOW:
            self.controller_show_hide(self.widget_restr_fixed,
                                      status,
                                      ControllerWorkSt.RESTR_FIXED)

    def controller_add_point(self, status):
        self._logger.debug(f'controller_add_point start with status {status}')

        if status == ControllerSt.SUBMIT:
            figure_coo = self.painted_figure.get_base_representation()
            self._project.add_figure(Point.from_coordinates(*figure_coo))
            status = ControllerSt.HIDE
        elif status == ControllerSt.MOUSE_ADD:
            figure_coo = self.painted_figure.get_base_representation()
            self._project.add_figure(Point.from_coordinates(*figure_coo))
            status = ControllerSt.HIDE

        elif status == ControllerSt.SHOW:
            self.field_x_add_point.setFocus()
            self.field_x_add_point.selectAll()
            self.painted_figure = Point.from_coordinates(
                self.field_x_add_point.value(),
                self.field_y_add_point.value()
            )
            self.creation_st = CreationSt.POINT_SET
        elif status == ControllerSt.HIDE:
            pass
        else:
            raise RuntimeError(f'Unexpected status {status}')

        if status == ControllerSt.HIDE:
            self.painted_figure = None
            self.creation_st = CreationSt.NOTHING

        if status == ControllerSt.HIDE or status == ControllerSt.SHOW:
            self.controller_show_hide(self.widget_add_point,
                                      status,
                                      ControllerWorkSt.ADD_POINT)

    def controller_add_segment(self, status):
        self._logger.debug(f'controller_add_segment start with status {status}')
        if status == ControllerSt.SUBMIT:
            figure_coo = self.painted_figure.get_base_representation()
            if float(self.field_x1_add_segment.value()) ==\
                float(self.field_x2_add_segment.value()) ==\
                float(self.field_y1_add_segment.value()) ==\
                float(self.field_y2_add_segment.value()):  # TODO: What a strange check??
                raise ValueError
            else:
                s = Segment.from_coordinates(*figure_coo)
                self._project.add_figure(s)
                status = ControllerSt.HIDE
        elif status == ControllerSt.MOUSE_ADD:
            figure_coo = self.painted_figure.get_base_representation()
            s = Segment.from_coordinates(*figure_coo)
            self._project.add_figure(s)
            status = ControllerSt.HIDE

        elif status == ControllerSt.SHOW:
            self.field_x1_add_segment.setFocus()
            self.field_x1_add_segment.selectAll()
            self.painted_figure = Segment.from_coordinates(
                self.field_x1_add_segment.value(),
                self.field_y1_add_segment.value(),
                self.field_x2_add_segment.value(),
                self.field_y2_add_segment.value()
            )
            self.creation_st = CreationSt.SEGMENT_START_SET
        elif status == ControllerSt.HIDE:
            pass
        else:
            raise RuntimeError(f'Unexpected status {status}')

        if status == ControllerSt.HIDE:
            self._logger.debug('Add segment status (2nd) == HIDE: start')
            self.painted_figure = None
            self.creation_st = CreationSt.NOTHING

        if status == ControllerSt.HIDE or status == ControllerSt.SHOW:
            self._logger.debug('Add segment status (2nd) == HIDE or SHOW: start')
            self.controller_show_hide(self.widget_add_segment,
                                      status,
                                      ControllerWorkSt.ADD_SEGMENT)

    @staticmethod
    def get_spot_type(binding):
        if isinstance(binding, SegmentStartBinding):
            return 'start'
        elif isinstance(binding, SegmentCenterBinding):
            return 'center'
        elif isinstance(binding, SegmentEndBinding):
            return 'end'
        else:
            raise TypeError

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

    @property
    def _footer_checkboxes(self) -> dict:
        checkboxes = dict()
        for name in dir(self):
            if name.startswith('checkbox_restr_'):
                checkboxes[name] = getattr(self, name)
        return checkboxes

    def animate(self):
        self.update()

    def paintEvent(self, event):
        # self._logger.debug('paintEvent')
        self._glwindow_proc.paint_all(
            event,
            self._project.figures,
            self.painted_figure
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x, y = self._glwindow_proc.to_real_xy(event.x(), event.y())

            if self.controller_work_st == ControllerWorkSt.ADD_POINT:
                if self.creation_st == CreationSt.POINT_SET:
                    self.controller_add_point(ControllerSt.MOUSE_ADD)

            elif self.controller_work_st == ControllerWorkSt.ADD_SEGMENT:
                if self.creation_st == CreationSt.SEGMENT_START_SET:
                    self.painted_figure.set_param('x1', x).set_param('y1', y)
                    self.creation_st = CreationSt.SEGMENT_END_SET
                    self.field_x2_add_segment.setFocus()
                    self.field_x2_add_segment.selectAll()
                elif self.creation_st == CreationSt.SEGMENT_END_SET:
                    self.controller_add_segment(ControllerSt.MOUSE_ADD)
                    self.painted_figure = None

    def mouseMoveEvent(self, event):
        x, y = self._glwindow_proc.to_real_xy(event.x(), event.y())

        if self.controller_work_st == ControllerWorkSt.ADD_POINT:
            self.painted_figure.set_param('x', x).set_param('y', y)
            self.field_x_add_point.setValue(x)
            self.field_y_add_point.setValue(y)
            # Select field with focus
            if self.field_x_add_point.hasFocus():
                self.field_x_add_point.selectAll()
            elif self.field_y_add_point.hasFocus():
                self.field_y_add_point.selectAll()

        elif self.controller_work_st == ControllerWorkSt.ADD_SEGMENT:
            if self.creation_st == CreationSt.SEGMENT_START_SET:
                self.painted_figure.set_param('x1', x).set_param('y1', y)
                self.field_x1_add_segment.setValue(x)
                self.field_y1_add_segment.setValue(y)
            elif self.creation_st == CreationSt.SEGMENT_END_SET:
                self.painted_figure.set_param('x2', x).set_param('y2', y)
                self.field_x2_add_segment.setValue(x)
                self.field_y2_add_segment.setValue(y)

            # Select field with focus
            if self.field_x1_add_segment.hasFocus():
                self.field_x1_add_segment.selectAll()
            elif self.field_y1_add_segment.hasFocus():
                self.field_y1_add_segment.selectAll()
            elif self.field_x2_add_segment.hasFocus():
                self.field_x2_add_segment.selectAll()
            elif self.field_y2_add_segment.hasFocus():
                self.field_y2_add_segment.selectAll()


        # Work with bindings
        if self.controller_work_st == ControllerWorkSt.RESTR_JOINT:
            allowed_bindings_types = (
                PointBinding,
                SegmentStartBinding, SegmentCenterBinding, SegmentEndBinding
            )
            # TODO: check all variants
        else:
            allowed_bindings_types = None

        self._glwindow_proc.handle_mouse_move_event(
            event,
            self._project.bindings,
            self._project.figures,
            allowed_bindings_types
        )

    def mouseReleaseEvent(self, event):
        self._logger.debug('mouseReleaseEvent: start')
        if event.button() == Qt.LeftButton:
            x, y = self._glwindow_proc.to_real_xy(event.x(), event.y())
            if self.choose == ChooseSt.CHOOSE:
                best_bindings = choose_best_bindings(self._project.bindings,
                                                     x,
                                                     y)
                if self.controller_work_st == \
                        ControllerWorkSt.RESTR_SEGMENTS_NORMAL:
                    self.controller_restr_segments_normal(ControllerSt.ADD,
                                                          best_bindings)
                elif self.controller_work_st == \
                    ControllerWorkSt.RESTR_JOINT:
                    self.controller_restr_joint(ControllerSt.ADD,
                                                best_bindings)
                elif self.controller_work_st == \
                        ControllerWorkSt.RESTR_FIXED:
                    self.controller_restr_fixed(ControllerSt.ADD,
                                                best_bindings)
                # elif self.controller_work_st == ControllerWorkSt.RES
                # else:
                #     raise RuntimeError(f'Unexpected state {self.controller_work_st}')



        # self._glwindow_proc.handle_mouse_release_event(event,
        #                                                self._project.bindings,
        #                                                self.choose,
        #                                                self.controller_work_st)

    def _trigger_widget(self, button, widget_name, show: bool = False):
        widget = getattr(self, widget_name)
        self._hide_footer_widgets()
        self._uncheck_left_buttons()
        self.painted_figure = None
        # self._interf ace_proc.trigger_button(button, show)
        self._interface_proc.trigger_widget(widget, show)

    def _hide_footer_widgets(self):
        for box in self._footer_checkboxes.values():
            if box.checkState() == Qt.Checked:
                box.toggle()
        for w_name, widget in self._footer_widgets.items():
            self._interface_proc.trigger_widget(widget, False)
        # self._logger('_hide_footer_widgets')
        self.field_x_add_point.setValue(0)
        self.field_y_add_point.setValue(0)
        self.field_x1_add_segment.setValue(0)
        self.field_y1_add_segment.setValue(0)
        self.field_x2_add_segment.setValue(0)
        self.field_y2_add_segment.setValue(0)

    def _uncheck_left_buttons(self):
        for b_name, button in self._left_buttons.items():
            self._interface_proc.trigger_button(button, False)

    def new(self, _=None):
        self.reset()
        self._project = CADProject()
        self._filename = None

    def exit(self, _=None):
        self._window.close()
        
    def reset(self, _=None):
        self._logger.debug('reset: start')

        self.controller_work_st = ControllerWorkSt.NOTHING
        self.choose = ChooseSt.NOTHING
        self.creation_st = CreationSt.NOTHING
        self.painted_figure = None

        self._hide_footer_widgets()
        self._uncheck_left_buttons()

    def save(self, _=None):
        if self._filename is None:
            self.save_as()
        else:
            self._project.save(self._filename)

    def save_as(self, _=None):
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить', '', 'SCAD Files (*.scad)')
        if filename:
            self._filename = filename
            self.save()

    def open(self, _=None):
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Открыть', '', 'SCAD Files (*.scad)')
        if filename:
            self._filename = filename
            self._project.load(self._filename)

    def undo(self, ev):
        self._logger.debug(f'Undo: ev = {ev}')
        try:
            self._project.undo()
        except ActionImpossible:
            # TODO: Status bar / inactive
            pass

    def redo(self, ev):
        self._logger.debug(f'Redo: ev = {ev}')
        try:
            self._project.redo()
        except ActionImpossible:
            # TODO: Status bar / inactive
            pass

    def _get_buttons_to_widgets_dict(self):
        buttons_to_widgets_dict = dict()
        for name in dir(self):
            if name.startswith('button_add_') \
                    or name.startswith('button_restr_'):
                widget_name = 'widget' + name[6:]
                if widget_name in dir(self):
                    buttons_to_widgets_dict[name] = widget_name
        return buttons_to_widgets_dict
