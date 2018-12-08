"""Module with main class of application that manage system and picture."""

from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt, QStringListModel
from logging import getLogger
import re

from glwindow_processing import GLWindowProcessor
from interface import InterfaceProcessor
from design import Ui_window
from states import ControllerWorkSt, ChooseSt, ControllerSt, CreationSt, ActionSt

from project import CADProject, ActionImpossible
from solve import CannotSolveSystemError
from figures import Point, Segment
from restrictions import (
    PointFixed,
    PointsJoint,
    SegmentFixed,
    SegmentAngleFixed,
    SegmentLengthFixed,
    SegmentSpotFixed,
    SegmentHorizontal,
    SegmentVertical,
    SegmentsParallel,
    SegmentsNormal,
    SegmentsSpotsJoint,
    SegmentsAngleBetweenFixed,
    PointOnSegmentFixed,
    PointOnSegmentLine,
    PointAndSegmentSpotJoint,
)
from bindings import (
    PointBinding,
    SegmentStartBinding,
    SegmentCenterBinding,
    SegmentEndBinding,
    SegmentsIntersectionBinding,
    FullSegmentBinding,
    choose_best_bindings
)


def get_spot_type(binding):
    if isinstance(binding, SegmentStartBinding):
        return 'start'
    elif isinstance(binding, SegmentCenterBinding):
        return 'center'
    elif isinstance(binding, SegmentEndBinding):
        return 'end'
    else:
        raise TypeError


class WindowContent(QOpenGLWidget, Ui_window):
    def __init__(self, window: QMainWindow):
        self._logger = getLogger('WindowContent')

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
        self._setup_useful_aliases()

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
        self.action_st = ActionSt.NOTHING

        self.choosed_bindings = []

        self.painted_figure = None  # Figure that is painted at this moment
        self.creation_st = CreationSt.NOTHING

        self._filename = None

        self._selected_binding = None

        self._selected_figure = None

    def _setup_useful_aliases(self):
        self._footer_widgets = dict()
        self._left_buttons = dict()
        self._footer_checkboxes = dict()

        for name in dir(self):
            if re.match(r'^checkbox_restr_', name):
                self._footer_checkboxes[name] = getattr(self, name)
            elif re.match(r'^button_(add|restr)_', name):
                self._left_buttons[name] = getattr(self, name)
            elif re.match(r'^widget_(add|restr)_', name):
                self._footer_widgets[name] = getattr(self, name)

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

        # List views
        self.widget_elements_table.clicked.connect(self.select_figure_on_plane)

    def select_figure_on_plane(self, item_idx):
        # I don't know why [0]
        figure_name = self.widget_elements_table.model().itemData(item_idx)[0]
        self._selected_figure = self._project.figures[figure_name]

    def change_painted_figure(self, field: str, value: float):
        if self.painted_figure is not None:
            self.painted_figure.set_param(field, value)
        # TODO: Move mouse

    def show_hide_controller(self, widget, controller_st, controller_work_st):
        if controller_st == ControllerSt.HIDE:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
            self.reset()
        if controller_st == ControllerSt.SHOW:
            widget.show()
            self.controller_work_st = controller_work_st
            self.choose = ChooseSt.CHOOSE

    def controller_add_point(self, status):
        self._logger.debug(f'controller_add_point start with status {status}')

        if status == ControllerSt.SUBMIT or status == ControllerSt.MOUSE_ADD:
            figure_coo = self.painted_figure.get_base_representation()
            self._project.add_figure(Point.from_coordinates(*figure_coo))
            status = ControllerSt.HIDE
            self._update_figures_list_view()

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
            self.show_hide_controller(self.widget_add_point,
                                      status,
                                      ControllerWorkSt.ADD_POINT)

    def controller_add_segment(self, status):

        self._logger.debug(f'controller_add_segment start with status {status}')
        if status == ControllerSt.SUBMIT or status == ControllerSt.MOUSE_ADD:
            figure_coo = self.painted_figure.get_base_representation()
            s = Segment.from_coordinates(*figure_coo)
            self._project.add_figure(s)
            status = ControllerSt.HIDE
            self._update_figures_list_view()

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
            self.painted_figure = None
            self.creation_st = CreationSt.NOTHING

        if status == ControllerSt.HIDE or status == ControllerSt.SHOW:
            self.show_hide_controller(
                self.widget_add_segment, status, ControllerWorkSt.ADD_SEGMENT)

    def controller_restr_segments_parallel(self, status: int):
        if status == ControllerSt.HIDE:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
        if status == ControllerSt.SHOW:
            self._hide_footer_widgets()
            self._uncheck_left_buttons()
            self.widget_restr_segments_parallel.show()
        if status == ControllerSt.SUBMIT:
            if not self.checkbox_restr_segments_parallel_1.checkState() or \
                    not self.checkbox_restr_segments_parallel_2.checkState():
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
            self.show_hide_controller(self.widget_restr_segments_normal,
                                      status,
                                      ControllerWorkSt.RESTR_SEGMENTS_NORMAL)

    def controller_restr_segment_length_fixed(self, status):
        if status == ControllerSt.SUBMIT:
            if not self.checkbox_restr_segment_length_fixed.checkState():
                pass
            else:
                pass
        else:
            self.show_hide_controller(self.widget_restr_segment_length_fixed,
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
            self.show_hide_controller(self.widget_restr_segment_horizontal,
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
            self.show_hide_controller(self.widget_restr_segment_angle_fixed,
                                      status,
                                      ControllerWorkSt.
                                      RESTR_SEGMENT_ANGLE_FIXED)

    def controller_restr_joint(self, status, bindings: list = None):
        if status == ControllerSt.ADD:
            for binding in bindings:
                if isinstance(
                    binding,
                    (
                        PointBinding,
                        SegmentStartBinding,
                        SegmentCenterBinding,
                        SegmentEndBinding
                    )
                ):
                    self.choosed_bindings.append(binding)
                    if len(self.choosed_bindings) == 1:
                        self.checkbox_restr_joint_1.toggle()
                    elif len(self.choosed_bindings) == 2:
                        self.checkbox_restr_joint_2.toggle()
                        self.choose = ChooseSt.NOTHING
                        self.submit_restr_joint.setFocus()
                    break
        elif status == ControllerSt.SUBMIT:
            if len(self.choosed_bindings) < 2:
                raise RuntimeError

            b1, b2 = self.choosed_bindings
            if isinstance(b1, PointBinding):
                if isinstance(b2, PointBinding):
                    restr = PointsJoint()
                else:
                    spot_type = get_spot_type(b2)
                    restr = PointAndSegmentSpotJoint(spot_type)
            else:
                spot_type_1 = get_spot_type(b1)
                if isinstance(b2, PointBinding):
                    b1, b2 = b2, b1
                    restr = PointAndSegmentSpotJoint(spot_type_1)
                else:
                    spot_type_2 = get_spot_type(b2)
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
            self.show_hide_controller(
                self.widget_restr_joint, status, ControllerWorkSt.RESTR_JOINT)

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
                if isinstance(
                    binding,
                    (
                        PointBinding,
                        SegmentStartBinding,
                        SegmentCenterBinding,
                        SegmentEndBinding,
                        FullSegmentBinding
                    )
                ):
                    self.choosed_bindings.append(binding)
                    if len(self.choosed_bindings) == 1:
                        self.checkbox_restr_fixed.toggle()
                        self.choose = ChooseSt.NOTHING
                        print('setting focus')
                        self.submit_restr_fixed.setFocus()
                    break

        elif status == ControllerSt.SUBMIT:
            if len(self.choosed_bindings) != 1:
                raise RuntimeError
            binding = self.choosed_bindings[0]
            figure_name = binding.get_object_names()[0]
            coo = self._project.figures[figure_name].get_base_representation()
            if isinstance(binding, PointBinding):
                restr = PointFixed(*coo)
            elif isinstance(binding, FullSegmentBinding):
                restr = SegmentFixed(*coo)
            else:  # Segment spot fixed  # TODO: check?
                binding_spot_type = get_spot_type(binding)
                if binding_spot_type == 'start':
                    coo = coo[:2]
                elif binding_spot_type == 'end':
                    coo = coo[2:]
                else:  # center
                    coo = coo[0] + coo[2] / 2, coo[1] + coo[3] / 2
                restr = SegmentSpotFixed(*coo, binding_spot_type)

            try:
                self._project.add_restriction(restr, (figure_name,))
            except CannotSolveSystemError:
                pass

            self.controller_work_st = ControllerWorkSt.NOTHING
            self.choosed_bindings = []
            status = ControllerSt.HIDE

        if status == ControllerSt.HIDE or status == ControllerSt.SHOW:
            self.show_hide_controller(
                self.widget_restr_fixed, status, ControllerWorkSt.RESTR_FIXED)

    def animate(self):
        self.update()

    def paintEvent(self, event):
        # self._logger.debug('paintEvent')

        self._glwindow_proc.paint_all(
            event,
            self._project.figures,
            self.painted_figure,
            self._selected_figure
        )

    def mousePressEvent(self, event):
        self._logger.debug('mousePressEvent: start')
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

            elif self.controller_work_st == ControllerWorkSt.NOTHING and\
                    self.creation_st == CreationSt.NOTHING:
                bindings = choose_best_bindings(self._project.bindings, x, y)
                if len(bindings) > 0:
                    self._selected_binding = bindings[0]
                    self.action_st = ActionSt.MOUSE_PRESSED

    def mouseMoveEvent(self, event):
        # self._logger.debug('mouseMoveEvent: start')
        x, y = self._glwindow_proc.to_real_xy(event.x(), event.y())

        if self.action_st == ActionSt.MOUSE_PRESSED:
            self.action_st = ActionSt.MOVE

        if self.action_st == ActionSt.MOVE:
            try:
                self._project.move_figure(self._selected_binding, x, y)
            except CannotSolveSystemError:
                self._project.rollback()

        if self.controller_work_st == ControllerWorkSt.ADD_POINT:
            if self.creation_st == CreationSt.POINT_SET:
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
                bindings = choose_best_bindings(self._project.bindings, x, y)

                if self.controller_work_st == \
                        ControllerWorkSt.RESTR_SEGMENTS_NORMAL:
                    self.controller_restr_segments_normal(
                        ControllerSt.ADD, bindings)

                elif self.controller_work_st == ControllerWorkSt.RESTR_JOINT:
                    self.controller_restr_joint(ControllerSt.ADD, bindings)

                elif self.controller_work_st == ControllerWorkSt.RESTR_FIXED:
                    self.controller_restr_fixed(ControllerSt.ADD, bindings)

            if self.action_st == ActionSt.MOVE:
                self._project.commit()
                self.action_st = ActionSt.NOTHING
                self.controller_work_st = ControllerWorkSt.NOTHING
                self.creation_st = CreationSt.NOTHING
            elif self.action_st == ActionSt.MOUSE_PRESSED:
                self.action_st = ActionSt.SELECT
                self.controller_work_st = ControllerWorkSt.NOTHING
                self.creation_st = CreationSt.NOTHING


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

        self._selected_figure = None

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
        self.choosed_bindings = []
        self._selected_binding = None
        self.action_st = ActionSt.NOTHING

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

    def _update_figures_list_view(self):
        figures_model = QStringListModel()
        for i, figure_name in enumerate(self._project.figures.keys()):
            figures_model.insertRow(i)
            figures_model.setData(figures_model.index(i), figure_name)
        self.widget_elements_table.setModel(figures_model)
