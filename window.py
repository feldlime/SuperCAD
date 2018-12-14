"""Module with main class of application that manage system and picture."""

from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt, QStringListModel, QItemSelectionModel
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QPushButton,
    QHBoxLayout, QVBoxLayout, QApplication)
from logging import getLogger
import re
from numpy import pi

from glwindow_processing import GLWindowProcessor
from interface import InterfaceProcessor
from design import Ui_window
from states import ControllerWorkSt, ControllerCmd, CreationSt, ActionSt

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
    # PointOnSegmentFixed,
    PointOnSegmentLine,
    PointAndSegmentSpotJoint,
    SegmentSpotAndPointJoint
)
from bindings import (
    PointBinding,
    SegmentSpotBinding,
    # SegmentsIntersectionBinding,
    FullSegmentBinding,
    choose_best_bindings,
    is_any_segment_binding,
    is_normal_point_binding,
    is_any_normal_binding
)


def find_first(lst, cond_fun):
    for elem in lst:
        if cond_fun(elem):
            return elem
    return None


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

        #Set focus on window for keyPressEvent
        self.setFocusPolicy(Qt.StrongFocus)

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

        self.action_st = ActionSt.NOTHING

        self.chosen_bindings = []

        self.painted_figure = None  # Figure that is painted at this moment
        self.creation_st = CreationSt.NOTHING

        self._filename = None

        self._selected_binding = None

        self._selected_figure_name = None

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
        self.setTabOrder(self.field_y2_add_segment,
                         self.field_length_add_segment)
        self.setTabOrder(self.field_length_add_segment,
                         self.field_angle_add_segment)
        self.setTabOrder(self.field_angle_add_segment, self.submit_add_segment)

    def _setup_handlers(self):

        # Left buttons
        self.button_add_point.clicked['bool'].connect(
            lambda ev: self.controller_add_point(ControllerCmd.SHOW)
        )
        self.button_add_segment.clicked['bool'].connect(
            lambda ev: self.controller_add_segment(ControllerCmd.SHOW)
        )
        self.button_restr_joint.clicked['bool'].connect(
            self.controller_restr_joint
        )
        self.button_restr_point_on_segment_line.clicked['bool'].connect(
            self.controller_restr_point_on_segment_line
        )
        self.button_restr_segments_parallel.clicked['bool'].connect(
            self.controller_restr_segments_parallel
        )
        self.button_restr_segments_normal.clicked['bool'].connect(
            self.controller_restr_segments_normal
        )
        self.button_restr_segment_vertical.clicked['bool'].connect(
            self.controller_restr_segment_vertical
        )
        self.button_restr_segment_horizontal.clicked['bool'].connect(
            self.controller_restr_segment_horizontal
        )
        self.button_restr_fixed.clicked['bool'].connect(
            self.controller_restr_fixed
        )
        self.button_restr_segment_length_fixed.clicked['bool'].connect(
            self.controller_restr_segment_length_fixed
        )
        self.button_restr_segment_angle_fixed.clicked['bool'].connect(
            self.controller_restr_segment_angle_fixed
        )
        self.button_restr_segments_angle_between_fixed.clicked['bool'].connect(
            self.controller_restr_segment_angle_between_fixed
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
        self.field_length_add_segment.valueChanged.connect(
            lambda new_value: self.change_painted_figure('length', new_value)
        )
        self.field_angle_add_segment.valueChanged.connect(
            lambda new_value: self.change_painted_figure('angle',
                                                         new_value*pi/180)
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
        self.action_delete.triggered['bool'].connect(self.delete)

        # List views
        self.widget_elements_table.clicked.connect(self.select_figure_on_plane)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            if self.controller_work_st == ControllerWorkSt.ADD_POINT:
                self.controller_add_point(ControllerCmd.SUBMIT)
            elif self.controller_work_st == ControllerWorkSt.ADD_SEGMENT:
                self.controller_add_segment(ControllerCmd.SUBMIT)
            elif ControllerWorkSt.is_restr(self.controller_work_st):
                name = None
                for name in dir(ControllerWorkSt):
                    if re.match('^RESTR_', name):
                        break
                if name:
                    controller_name = f'controller_{name.lower()}'
                    getattr(self, controller_name)(ControllerCmd.SUBMIT)

    def field_update(self):
        if isinstance(self.painted_figure, Point):
            self.controller_add_point(ControllerCmd.MOVE)
        elif isinstance(self.painted_figure, Segment):
            self.controller_add_segment(ControllerCmd.MOVE)

    def select_figure_on_plane(self, item_idx):
        # I don't know why [0]
        figure_name = self.widget_elements_table.model().itemData(item_idx)[0]
        self._selected_figure_name = figure_name

    def select_figure_on_list_view(self):
        self.widget_elements_table.clearSelection()
        if self._selected_figure_name is not None:
            model = self.widget_elements_table.model()
            i = 0
            while True:
                index = model.index(i)
                item_data = model.itemData(index)
                if item_data:
                    if item_data[0] == self._selected_figure_name:
                        self.widget_elements_table.selectionModel().select(index, QItemSelectionModel.Select)
                        break
                else:
                    break
                i += 1
            self.change_selected_figure()

    def change_painted_figure(self, field: str, value: float):
        if self.painted_figure is not None:
            self.painted_figure.set_param(field, value)
        # TODO: Move mouse

    def change_selected_figure(self):
        # pass
        self.painted_figure = self._project.figures.pop(
            self._selected_figure_name)
        if isinstance(self.painted_figure, Point):
            self.controller_add_point(ControllerCmd.MOVE)
        elif isinstance(self.painted_figure, Segment):
            self.controller_add_segment(ControllerCmd.MOVE)

    # ======================== Controllers ==================

    def controller_add_point(self, cmd):
        self._logger.debug(f'controller_add_point start with status {cmd}')

        if cmd == ControllerCmd.SUBMIT:
            figure_coo = self.painted_figure.get_base_representation()
            self._project.add_figure(Point.from_coordinates(*figure_coo))
            self.reset()
            self._update_figures_list_view()

        elif cmd == ControllerCmd.SHOW:
            self.field_x_add_point.setFocus()
            self.field_x_add_point.selectAll()
            self.painted_figure = Point.from_coordinates(
                self.field_x_add_point.value(),
                self.field_y_add_point.value()
            )
            self.creation_st = CreationSt.POINT_SET
            self.widget_add_point.show()
            self.submit_add_point.show()
            self.controller_work_st = ControllerWorkSt.ADD_POINT

        elif cmd == ControllerCmd.MOVE:
            self.field_x_add_point.setFocus()
            self.field_x_add_point.selectAll()
            choo = self.painted_figure.get_base_representation()
            self.field_x_add_point.setValue(choo[0])
            self.field_y_add_point.setValue(-1*choo[1])
            self.widget_add_point.show()
            self.submit_add_point.hide()

        elif cmd == ControllerCmd.HIDE:
            self.reset()

    def controller_add_segment(self, cmd):
        self._logger.debug(f'controller_add_segment start with status {cmd}')

        if cmd == ControllerCmd.SUBMIT:
            figure_coo = self.painted_figure.get_base_representation()
            s = Segment.from_coordinates(*figure_coo)
            self._project.add_figure(s)
            self.reset()
            self._update_figures_list_view()

        elif cmd == ControllerCmd.SHOW:
            self.field_x1_add_segment.setFocus()
            self.field_x1_add_segment.selectAll()
            if self.field_length_add_segment.value() != 0:
                self.painted_figure = Segment.from_coordinates(
                    self.field_x1_add_segment.value(),
                    self.field_y1_add_segment.value(),
                    self.field_x2_add_segment.value(),
                    self.field_y2_add_segment.value(),
                )
            else:
                self.painted_figure = Segment(
                    start=(
                        self.field_x1_add_segment.value(),
                        self.field_y1_add_segment.value()
                    ),
                    angle=self.field_length_add_segment.value(),
                    length=self.field_angle_add_segment.value()
                )
            self.creation_st = CreationSt.SEGMENT_START_SET
            self.widget_add_segment.show()
            self.submit_add_segment.show()
            self.controller_work_st = ControllerWorkSt.ADD_SEGMENT

        elif cmd == ControllerCmd.MOVE:
                    self.field_x1_add_segment.setFocus()
                    self.field_x1_add_segment.selectAll()
                    choo = self.painted_figure.get_params()
                    self.field_x1_add_segment.setValue(choo['x1']),
                    self.field_y1_add_segment.setValue(choo['y1']),
                    self.field_x2_add_segment.setValue(choo['x2']),
                    self.field_y2_add_segment.setValue(choo['y2']),
                    self.field_length_add_segment.setValue(choo['length'])
                    self.field_angle_add_segment.setValue(choo['angle']*180/pi)
                    self.widget_add_segment.show()
                    self.submit_add_segment.hide()

        elif cmd == ControllerCmd.HIDE:
            self.reset()

    def controller_restr_joint(self, cmd, bindings: list = None):
        def get_restr_fun(b1, b2):
            if isinstance(b1, PointBinding):
                if isinstance(b2, PointBinding):
                    restr = PointsJoint()
                else:
                    restr = PointAndSegmentSpotJoint(b2.spot_type)
            else:
                if isinstance(b2, PointBinding):
                    restr = SegmentSpotAndPointJoint(b1.spot_type)
                else:
                    restr = SegmentsSpotsJoint(b1.spot_type, b2.spot_type)
            return restr

        self._controller_restr_two_objects(
            'joint',
            cmd,
            bindings,
            get_restr_fun,
            (is_normal_point_binding, is_normal_point_binding)
        )

    def controller_restr_point_on_segment_line(
            self, cmd, bindings: list = None):
        def get_restr_fun(_b1, _b2):
            return PointOnSegmentLine()

        self._controller_restr_two_objects(
            'point_on_segment_line',
            cmd,
            bindings,
            get_restr_fun,
            (lambda b: isinstance(b, PointBinding), is_any_segment_binding)
        )

    def controller_restr_segments_parallel(self, cmd, bindings: list = None):
        def get_restr_fun(_b1, _b2):
            return SegmentsParallel()

        self._controller_restr_two_objects(
            'segments_parallel',
            cmd,
            bindings,
            get_restr_fun,
            (is_any_segment_binding, is_any_segment_binding)
        )

    def controller_restr_segments_normal(self, cmd, bindings: list = None):
        def get_restr_fun(_b1, _b2):
            return SegmentsNormal()

        self._controller_restr_two_objects(
            'segments_normal',
            cmd,
            bindings,
            get_restr_fun,
            (is_any_segment_binding, is_any_segment_binding)
        )

    def controller_restr_segment_vertical(self, cmd, bindings: list = None):
        def get_restr_fun(_binding):
            return SegmentVertical()

        self._controller_restr_single_object(
            'segment_vertical',
            cmd,
            bindings,
            get_restr_fun,
            is_any_segment_binding
        )

    def controller_restr_segment_horizontal(self, cmd, bindings: list = None):
        def get_restr_fun(_binding):
            return SegmentHorizontal()

        self._controller_restr_single_object(
            'segment_horizontal',
            cmd,
            bindings,
            get_restr_fun,
            is_any_segment_binding
        )

    def controller_restr_fixed(self, cmd, bindings: list = None):
        def get_restr_fun(binding):
            figure_name = binding.get_object_names()[0]
            coo = self._project.figures[figure_name].get_base_representation()
            if isinstance(binding, PointBinding):
                restr = PointFixed(*coo)
            elif isinstance(binding, FullSegmentBinding):
                restr = SegmentFixed(*coo)
            elif isinstance(binding, SegmentSpotBinding):
                binding_spot_type = binding.spot_type
                if binding_spot_type == 'start':
                    coo = coo[:2]
                elif binding_spot_type == 'end':
                    coo = coo[2:]
                else:  # center
                    coo = coo[0] + coo[2] / 2, coo[1] + coo[3] / 2
                restr = SegmentSpotFixed(*coo, binding_spot_type)
            else:
                raise RuntimeError(f'Unexpected binding type {type(binding)}')
            return restr

        self._controller_restr_single_object(
            'fixed',
            cmd,
            bindings,
            get_restr_fun,
            is_any_normal_binding
        )

    def controller_restr_segment_length_fixed(
            self, cmd, bindings: list = None):
        def get_restr_fun(binding):
            segment_name = binding.get_object_names()[0]
            length = self._project.figures[segment_name].get_params()['length']
            return SegmentLengthFixed(length)

        self._controller_restr_single_object(
            'segment_length_fixed',
            cmd,
            bindings,
            get_restr_fun,
            is_any_segment_binding
        )

    def controller_restr_segment_angle_fixed(self, cmd, bindings: list = None):
        def get_restr_fun(binding):
            segment_name = binding.get_object_names()[0]
            angle = self._project.figures[segment_name].get_params()['angle']
            return SegmentAngleFixed(angle)

        self._controller_restr_single_object(
            'segment_angle_fixed',
            cmd,
            bindings,
            get_restr_fun,
            is_any_segment_binding
        )

    def controller_restr_segment_angle_between_fixed(
            self, cmd, bindings: list = None):
        # TODO
        pass

    def _controller_restr_single_object(self, name, cmd, bindings,
                                        get_restr_fun, check_binding_func):
        if cmd == ControllerCmd.STEP:
            binding = find_first(bindings, check_binding_func)
            if binding:
                if len(self.chosen_bindings) == 0:
                    self.chosen_bindings.append(binding)
                    getattr(self, f'checkbox_restr_{name}').toggle()

        elif cmd == ControllerCmd.SUBMIT:
            if len(self.chosen_bindings) != 1:
                raise RuntimeError
            binding = self.chosen_bindings[0]
            figure_name = binding.get_object_names()[0]
            restr = get_restr_fun(binding)
            try:
                self._project.add_restriction(restr, (figure_name,))
            except CannotSolveSystemError:
                pass

            self.controller_work_st = ControllerWorkSt.NOTHING
            self.chosen_bindings = []
            self.reset()

        elif cmd == ControllerCmd.SHOW:
            status = getattr(ControllerWorkSt, f'restr_{name}'.upper())
            widget = getattr(self, f'widget_restr_{name}')
            widget.show()
            self.controller_work_st = status

        elif cmd == ControllerCmd.HIDE:
            self.reset()

    def _controller_restr_two_objects(self, name, cmd, bindings,
                                      get_restr_fun, check_binding_funcs):
        if cmd == ControllerCmd.STEP:
            if len(self.chosen_bindings) == 0:
                binding = find_first(bindings, check_binding_funcs[0])
                if binding:
                    self.chosen_bindings.append(binding)
                    getattr(self, f'checkbox_restr_{name}_1').toggle()
            elif len(self.chosen_bindings) == 1:
                binding = find_first(bindings, check_binding_funcs[0])
                if binding:
                    self.chosen_bindings.append(binding)
                    getattr(self, f'checkbox_restr_{name}_2').toggle()

        elif cmd == ControllerCmd.SUBMIT:
            if len(self.chosen_bindings) != 2:
                raise RuntimeError
            b1, b2 = self.chosen_bindings
            f1_name = b1.get_object_names()[0]
            f2_name = b2.get_object_names()[0]
            restr = get_restr_fun(b1, b2)
            try:
                self._project.add_restriction(restr, (f1_name, f2_name))
            except CannotSolveSystemError:
                pass

            self.controller_work_st = ControllerWorkSt.NOTHING
            self.chosen_bindings = []
            self.reset()

        elif cmd == ControllerCmd.SHOW:
            status = getattr(ControllerWorkSt, f'restr_{name}'.upper())
            widget = getattr(self, f'widget_restr_{name}')
            widget.show()
            self.controller_work_st = status

        elif cmd == ControllerCmd.HIDE:
            self.reset()

    # ====================================== Events ========================
    def animate(self):
        self.update()

    def paintEvent(self, event):
        # self._logger.debug('paintEvent')

        selected_figure = None
        if self._selected_figure_name is not None:
            selected_figure = self._project.figures[self._selected_figure_name]

        self._glwindow_proc.paint_all(
            event,
            self._project.figures,
            self.painted_figure,
            selected_figure
        )

    def mousePressEvent(self, event):
        self._logger.debug('mousePressEvent: start')
        if event.button() == Qt.LeftButton:
            x, y = self._glwindow_proc.to_real_xy(event.x(), event.y())

            if self.controller_work_st == ControllerWorkSt.ADD_POINT:
                if self.creation_st == CreationSt.POINT_SET:
                    self.controller_add_point(ControllerCmd.SUBMIT)

            elif self.controller_work_st == ControllerWorkSt.ADD_SEGMENT:
                if self.creation_st == CreationSt.SEGMENT_START_SET:
                    self.painted_figure.set_param('x1', x).set_param('y1', y)
                    self.creation_st = CreationSt.SEGMENT_END_SET
                    self.field_x2_add_segment.setFocus()
                    self.field_x2_add_segment.selectAll()
                elif self.creation_st == CreationSt.SEGMENT_END_SET:
                    self.controller_add_segment(ControllerCmd.SUBMIT)
                    self.painted_figure = None

            elif self.controller_work_st == ControllerWorkSt.NOTHING and\
                    self.creation_st == CreationSt.NOTHING:
                bindings = choose_best_bindings(self._project.bindings, x, y)
                if len(bindings) > 0:
                    self._selected_binding = bindings[0]
                    self.action_st = ActionSt.BINDING_PRESSED

    def mouseMoveEvent(self, event):
        # self._logger.debug('mouseMoveEvent: start')
        x, y = self._glwindow_proc.to_real_xy(event.x(), event.y())

        if self.action_st == ActionSt.BINDING_PRESSED and \
                self._selected_figure_name is not None:
            self.action_st = ActionSt.MOVE

        if self.action_st == ActionSt.MOVE:
            try:
                self._project.move_figure(self._selected_binding, x, y)
                self.field_update()
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
            allowed_bindings_types = (PointBinding, SegmentSpotBinding)
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

            if self.controller_work_st != ControllerWorkSt.NOTHING:
                # Make restriction step
                bindings = choose_best_bindings(self._project.bindings, x, y)
                for name in dir(ControllerWorkSt):
                    if re.match(r'^RESTR_', name):
                        status = getattr(ControllerWorkSt, name)
                        if self.controller_work_st == status:
                            controller = getattr(
                                self,
                                f'controller_{name.lower()}'
                            )
                            controller(ControllerCmd.STEP, bindings)

            if self.action_st == ActionSt.MOVE:
                self._project.commit()
                self.action_st = ActionSt.NOTHING
            elif self.action_st == ActionSt.BINDING_PRESSED:
                selected_figures = self._selected_binding.get_object_names()
                self._selected_binding = None
                if len(selected_figures) == 1:
                    self._selected_figure_name = selected_figures[0]
                    self.select_figure_on_list_view()
                self.action_st = ActionSt.NOTHING

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

        self._selected_figure_name = None

    def _uncheck_left_buttons(self):
        for b_name, button in self._left_buttons.items():
            self._interface_proc.trigger_button(button, False)

    def delete(self, _=None):
        print('delete')
        if self._selected_figure_name is not None:
            self._project.remove_figure(self._selected_figure_name)
            self._selected_figure_name = None

    def new(self, _=None):
        self.reset()
        self._project = CADProject()
        self._filename = None

    def exit(self, _=None):
        self._window.close()

    def reset(self, _=None):
        self._logger.debug('reset: start')

        self.controller_work_st = ControllerWorkSt.NOTHING
        self.creation_st = CreationSt.NOTHING
        self.painted_figure = None
        self.chosen_bindings = []
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
