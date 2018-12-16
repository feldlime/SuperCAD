"""Module with main class of application that manage system and picture."""

from logging import getLogger
import re
from typing import Dict, Optional


from numpy import pi as np_pi

from PyQt5.QtWidgets import (
    QOpenGLWidget,
    QMainWindow,
    QFileDialog,
    QTreeWidgetItem,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QBrush, QColor, QPainter, QPaintEvent

import paint
from design import Ui_window
from states import ControllerSt, ControllerCmd, CreationSt, ActionSt

from project import CADProject, ActionImpossible
from solve import CannotSolveSystemError
from figures import Figure, Point, Segment
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
    # SegmentsAngleBetweenFixed,
    # PointOnSegmentFixed,
    PointOnSegmentLine,
    PointAndSegmentSpotJoint,
    SegmentSpotAndPointJoint,
)
from bindings import (
    PointBinding,
    SegmentSpotBinding,
    # SegmentsIntersectionBinding,
    FullSegmentBinding,
    choose_best_bindings,
    is_any_segment_binding,
    is_normal_point_binding,
    is_any_normal_binding,
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

        # Setup basic UI - from design.py
        self.setupUi(self._window)

        # Init GLWidget: self.work_plane - QOpenGLWidget that was created into
        # setupUi in design.py
        super().__init__(self.work_plane)

        # Set additional private attributes
        self._setup_useful_aliases()

        # Setup special UI - method _setup_ui
        self._setup_ui()

        # Setup handlers (only for ui, because handlers for glwindow are
        # default methods)
        self._setup_handlers()

        # States
        self.controller_st = ControllerSt.NOTHING  # Left buttons controllers
        self.creation_st = CreationSt.NOTHING  # Stages of figures creation
        self.action_st = ActionSt.NOTHING  # Moving and changing figures

        # Special attributes
        self._mouse_xy = (0, 0)
        self._selected_figure_name = None  # Name of figure that selected now
        self._selected_restriction_name = None
        self._created_figure = None  # Figure that is created at this moment
        self._highlighted_figures = []
        self._moved_binding = None  # Binding used to move figure
        self._restriction_bindings = []  # Selected bindings for restriction
        self._current_bindings = []
        self._filename = None

    def _setup_useful_aliases(self):
        self._footer_widgets = dict()
        self._left_buttons = dict()
        self._footer_checkboxes = dict()
        self._footer_fields = dict()

        for name in dir(self):
            if re.match(r'^checkbox_restr_', name):
                self._footer_checkboxes[name] = getattr(self, name)
            elif re.match(r'^button_(add|restr)_', name):
                self._left_buttons[name] = getattr(self, name)
            elif re.match(r'^widget_(add|restr)_', name):
                self._footer_widgets[name] = getattr(self, name)
            elif re.match(r'^field_.*_add', name):
                self._footer_fields[name] = getattr(self, name)

    def _setup_ui(self):
        self._logger.debug('setup_ui start')

        self.widget_elements_table.show()
        self._reset_footer_widgets()
        self.action_show_elements_table.triggered['bool'].connect(
            lambda ev: self.widget_elements_table.show()
            if ev
            else self.widget_elements_table.hide()
        )

        self.widget_elements_table.setHeaderHidden(True)
        self.widget_elements_table_figures = QTreeWidgetItem(['Figures'])
        self.widget_elements_table_restrictions = QTreeWidgetItem(
            ['Restrictions']
        )
        self.widget_elements_table.addTopLevelItems(
            [
                self.widget_elements_table_figures,
                self.widget_elements_table_restrictions,
            ]
        )

        # Setting tab order. Can do it into designer and remove from here

        # Add point
        self.setTabOrder(self.field_x_add_point, self.field_y_add_point)
        # Add segment
        self.setTabOrder(self.field_x1_add_segment, self.field_y1_add_segment)
        self.setTabOrder(self.field_y1_add_segment, self.field_x2_add_segment)
        self.setTabOrder(self.field_x2_add_segment, self.field_y2_add_segment)
        self.setTabOrder(
            self.field_y2_add_segment, self.field_length_add_segment
        )
        self.setTabOrder(
            self.field_length_add_segment, self.field_angle_add_segment
        )

        # GLWidget settings
        self.elapsed = 0
        self.setAutoFillBackground(True)
        self.setMouseTracking(True)
        self.setGeometry(
            QRect(0, 0, self.work_plane.width(), self.work_plane.height())
        )
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        # Set focus on window for keyPressEvent
        self.setFocusPolicy(Qt.StrongFocus)

    def _setup_handlers(self):
        # Left buttons
        self.button_add_point.clicked['bool'].connect(
            lambda ev: self.controller_add_point(ControllerCmd.SHOW)
        )
        self.button_add_segment.clicked['bool'].connect(
            lambda ev: self.controller_add_segment(ControllerCmd.SHOW)
        )
        self.button_restr_joint.clicked['bool'].connect(
            lambda ev: self.controller_restr_joint(ControllerCmd.SHOW)
        )
        self.button_restr_point_on_segment_line.clicked['bool'].connect(
            lambda ev: self.controller_restr_point_on_segment_line(
                ControllerCmd.SHOW
            )
        )
        self.button_restr_segments_parallel.clicked['bool'].connect(
            lambda ev: self.controller_restr_segments_parallel(
                ControllerCmd.SHOW
            )
        )
        self.button_restr_segments_normal.clicked['bool'].connect(
            lambda ev: self.controller_restr_segments_normal(
                ControllerCmd.SHOW
            )
        )
        self.button_restr_segment_vertical.clicked['bool'].connect(
            lambda ev: self.controller_restr_segment_vertical(
                ControllerCmd.SHOW
            )
        )
        self.button_restr_segment_horizontal.clicked['bool'].connect(
            lambda ev: self.controller_restr_segment_horizontal(
                ControllerCmd.SHOW
            )
        )
        self.button_restr_fixed.clicked['bool'].connect(
            lambda ev: self.controller_restr_fixed(ControllerCmd.SHOW)
        )
        self.button_restr_segment_length_fixed.clicked['bool'].connect(
            lambda ev: self.controller_restr_segment_length_fixed(
                ControllerCmd.SHOW
            )
        )
        self.button_restr_segment_angle_fixed.clicked['bool'].connect(
            lambda ev: self.controller_restr_segment_angle_fixed(
                ControllerCmd.SHOW
            )
        )
        self.button_restr_segments_angle_between_fixed.clicked['bool'].connect(
            lambda ev: self.controller_restr_segment_angle_between_fixed(
                ControllerCmd.SHOW
            )
        )

        # Fields
        self.field_x_add_point.valueChanged.connect(
            lambda new_value: self.change_created_or_selected_figure(
                'x', new_value
            )
        )
        self.field_y_add_point.valueChanged.connect(
            lambda new_value: self.change_created_or_selected_figure(
                'y', new_value
            )
        )
        self.field_x1_add_segment.valueChanged.connect(
            lambda new_value: self.change_created_or_selected_figure(
                'x1', new_value
            )
        )
        self.field_y1_add_segment.valueChanged.connect(
            lambda new_value: self.change_created_or_selected_figure(
                'y1', new_value
            )
        )
        self.field_x2_add_segment.valueChanged.connect(
            lambda new_value: self.change_created_or_selected_figure(
                'x2', new_value
            )
        )
        self.field_y2_add_segment.valueChanged.connect(
            lambda new_value: self.change_created_or_selected_figure(
                'y2', new_value
            )
        )
        self.field_length_add_segment.valueChanged.connect(
            lambda new_value: self.change_created_or_selected_figure(
                'length', new_value
            )
        )
        self.field_angle_add_segment.valueChanged.connect(
            lambda new_value: self.change_created_or_selected_figure(
                'angle', new_value * np_pi / 180
            )
        )

        # Actions
        self.action_undo.triggered['bool'].connect(self.undo)
        self.action_redo.triggered['bool'].connect(self.redo)
        self.action_save.triggered['bool'].connect(self.save)
        self.action_save_as.triggered['bool'].connect(self.save_as)
        self.action_open.triggered['bool'].connect(self.open)
        self.action_new.triggered['bool'].connect(self.new)
        self.action_exit.triggered['bool'].connect(self.exit)
        self.action_delete.triggered['bool'].connect(self.delete)

        # List views
        self.widget_elements_table.clicked.connect(
            self.handle_elements_table_click
        )

    @property
    def _center(self) -> tuple:
        return self.width() // 2, self.height() // 2

    def _to_real_xy(self, x, y) -> tuple:
        return x - self._center[0], -(y - self._center[1])

    def _update_fields(self):
        self._logger.debug('update fields')
        if self._created_figure is not None:
            figure = self._created_figure
        elif self._selected_figure_name is not None:
            figure = self._project.figures[self._selected_figure_name]
        else:
            return

        def set_with_block(field, value):
            field.blockSignals(True)
            field.setValue(value)
            field.blockSignals(False)

        if isinstance(figure, Point):
            params = figure.get_params()
            set_with_block(self.field_x_add_point, params['x'])
            set_with_block(self.field_y_add_point, params['y'])

            # Select field with focus
            if self.field_x_add_point.hasFocus():
                self.field_x_add_point.selectAll()
            elif self.field_y_add_point.hasFocus():
                self.field_y_add_point.selectAll()

        elif isinstance(figure, Segment):
            params = figure.get_params()
            set_with_block(self.field_x1_add_segment, params['x1'])
            set_with_block(self.field_y1_add_segment, params['y1'])
            set_with_block(self.field_x2_add_segment, params['x2'])
            set_with_block(self.field_y2_add_segment, params['y2'])
            set_with_block(self.field_length_add_segment, params['length'])
            set_with_block(
                self.field_angle_add_segment, params['angle'] * 180 / np_pi
            )

            # Select field with focus
            if self.field_x1_add_segment.hasFocus():
                self.field_x1_add_segment.selectAll()
            elif self.field_y1_add_segment.hasFocus():
                self.field_y1_add_segment.selectAll()
            elif self.field_x2_add_segment.hasFocus():
                self.field_x2_add_segment.selectAll()
            elif self.field_y2_add_segment.hasFocus():
                self.field_y2_add_segment.selectAll()
            elif self.field_length_add_segment.hasFocus():
                self.field_length_add_segment.selectAll()
            elif self.field_angle_add_segment.hasFocus():
                self.field_angle_add_segment.selectAll()

    def handle_elements_table_click(self, item_idx):
        # I don't know why [0]
        object_name = self.widget_elements_table.model().itemData(item_idx)[0]
        if object_name in self._project.figures:
            self._reset_behind_statuses()
            self._selected_figure_name = object_name
            self.begin_figure_selection()
        elif object_name in self._project.restrictions:
            self._reset_behind_statuses()
            self._selected_restriction_name = object_name
            restr = self._project.restrictions[object_name]
            self._highlighted_figures = [
                self._project.figures[f_name]
                for f_name in restr.get_object_names()
            ]
            self.update()

    def select_element_on_tree(self):
        self.widget_elements_table.clearSelection()
        if self._selected_figure_name is not None:
            figure_to_select = self.widget_elements_table.findItems(
                str(self._selected_figure_name),
                # Qt.MatchExactly,
                Qt.MatchRecursive,
            )
            self.widget_elements_table.setCurrentItem(figure_to_select[0])
            # if self._project.bindings.key()
        self.begin_figure_selection()

    def change_created_or_selected_figure(self, field: str, value: float):
        # For angle value in radians
        if self._created_figure is not None:
            self._created_figure.set_param(field, value)
        elif self._selected_figure_name is not None:
            self._project.change_figure(
                self._selected_figure_name, field, value
            )

        self.update()

    def begin_figure_selection(self):
        if self._selected_figure_name is None:
            return
        selected_figure_name = self._selected_figure_name
        self.reset()
        self._selected_figure_name = selected_figure_name
        self.action_st = ActionSt.SELECTED
        self._update_fields()
        figure = self._project.figures[self._selected_figure_name]
        if isinstance(figure, Point):
            self.controller_add_point(ControllerCmd.SHOW)
        elif isinstance(figure, Segment):
            self.controller_add_segment(ControllerCmd.SHOW)
        self.update()

    # ======================== Controllers ==================

    def controller_add_point(self, cmd):
        self._logger.debug(f'controller_add_point start with status {cmd}')

        if cmd == ControllerCmd.SUBMIT:
            figure_coo = self._created_figure.get_base_representation()
            self._project.add_figure(Point.from_coordinates(*figure_coo))
            self.reset()
            self._update_list_view()

            self.controller_add_point(ControllerCmd.SHOW)

        elif cmd == ControllerCmd.SHOW:
            if self.action_st == ActionSt.NOTHING:
                self._reset_behind_statuses()
                self.controller_st = ControllerSt.ADD_POINT
                self.creation_st = CreationSt.POINT_SET
                self._created_figure = Point.from_coordinates(
                    self.field_x_add_point.value(),
                    self.field_y_add_point.value(),
                )

            self.button_add_point.setChecked(True)
            self.widget_add_point.show()
            self.field_x_add_point.setFocus()
            self.field_x_add_point.selectAll()

        elif cmd == ControllerCmd.HIDE:
            self.reset()

        self.update()

    def controller_add_segment(self, cmd):
        self._logger.debug(f'controller_add_segment start with status {cmd}')

        if cmd == ControllerCmd.SUBMIT:
            figure_coo = self._created_figure.get_base_representation()
            s = Segment.from_coordinates(*figure_coo)
            self._project.add_figure(s)
            self.reset()
            self._update_list_view()

            self.controller_add_segment(ControllerCmd.SHOW)

        elif cmd == ControllerCmd.SHOW:
            if self.action_st == ActionSt.NOTHING:
                self._reset_behind_statuses()
                self.controller_st = ControllerSt.ADD_SEGMENT
                self.creation_st = CreationSt.SEGMENT_START_SET

                self._created_figure = Segment.from_coordinates(
                    self.field_x1_add_segment.value(),
                    self.field_y1_add_segment.value(),
                    self.field_x2_add_segment.value(),
                    self.field_y2_add_segment.value(),
                )

            self.button_add_segment.setChecked(True)
            self.widget_add_segment.show()
            self.field_x1_add_segment.setFocus()
            self.field_x1_add_segment.selectAll()

        elif cmd == ControllerCmd.HIDE:
            self.reset()

        self.update()

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
            (is_normal_point_binding, is_normal_point_binding),
        )

    def controller_restr_point_on_segment_line(
        self, cmd, bindings: list = None
    ):
        def get_restr_fun(_b1, _b2):
            return PointOnSegmentLine()

        self._controller_restr_two_objects(
            'point_on_segment_line',
            cmd,
            bindings,
            get_restr_fun,
            (lambda b: isinstance(b, PointBinding), is_any_segment_binding),
        )

    def controller_restr_segments_parallel(self, cmd, bindings: list = None):
        def get_restr_fun(_b1, _b2):
            return SegmentsParallel()

        self._controller_restr_two_objects(
            'segments_parallel',
            cmd,
            bindings,
            get_restr_fun,
            (is_any_segment_binding, is_any_segment_binding),
        )

    def controller_restr_segments_normal(self, cmd, bindings: list = None):
        def get_restr_fun(_b1, _b2):
            return SegmentsNormal()

        self._controller_restr_two_objects(
            'segments_normal',
            cmd,
            bindings,
            get_restr_fun,
            (is_any_segment_binding, is_any_segment_binding),
        )

    def controller_restr_segment_vertical(self, cmd, bindings: list = None):
        def get_restr_fun(_binding):
            return SegmentVertical()

        self._controller_restr_single_object(
            'segment_vertical',
            cmd,
            bindings,
            get_restr_fun,
            is_any_segment_binding,
        )

    def controller_restr_segment_horizontal(self, cmd, bindings: list = None):
        def get_restr_fun(_binding):
            return SegmentHorizontal()

        self._controller_restr_single_object(
            'segment_horizontal',
            cmd,
            bindings,
            get_restr_fun,
            is_any_segment_binding,
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
                    coo = (coo[0] + coo[2]) / 2, (coo[1] + coo[3]) / 2
                restr = SegmentSpotFixed(*coo, binding_spot_type)
            else:
                raise RuntimeError(f'Unexpected binding type {type(binding)}')
            return restr

        self._controller_restr_single_object(
            'fixed', cmd, bindings, get_restr_fun, is_any_normal_binding
        )

    def controller_restr_segment_length_fixed(
        self, cmd, bindings: list = None
    ):
        def get_restr_fun(binding):
            segment_name = binding.get_object_names()[0]
            length = self._project.figures[segment_name].get_params()['length']
            return SegmentLengthFixed(length)

        self._controller_restr_single_object(
            'segment_length_fixed',
            cmd,
            bindings,
            get_restr_fun,
            is_any_segment_binding,
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
            is_any_segment_binding,
        )

    def controller_restr_segment_angle_between_fixed(
        self, cmd, bindings: list = None
    ):
        # TODO
        pass

    def _controller_restr_single_object(
        self, name, cmd, bindings, get_restr_fun, check_binding_func
    ):
        if cmd == ControllerCmd.STEP:
            binding = find_first(bindings, check_binding_func)
            if binding:
                if len(self._restriction_bindings) == 0:
                    self._restriction_bindings.append(binding)
                    getattr(self, f'checkbox_restr_{name}').toggle()

        elif cmd == ControllerCmd.SUBMIT:
            if len(self._restriction_bindings) != 1:
                raise RuntimeError
            binding = self._restriction_bindings[0]
            figure_name = binding.get_object_names()[0]
            restr = get_restr_fun(binding)
            try:
                self._project.add_restriction(restr, (figure_name,))
            except CannotSolveSystemError:
                pass
            self.reset()
            self._update_list_view()

            controller_name = f'controller_restr_{name}'
            getattr(self, controller_name)(ControllerCmd.SHOW)

        elif cmd == ControllerCmd.SHOW:
            self._reset_behind_statuses()
            status = getattr(ControllerSt, f'restr_{name}'.upper())
            widget = getattr(self, f'widget_restr_{name}')
            widget.show()
            button = getattr(self, f'button_restr_{name}')
            button.setChecked(True)
            self.controller_st = status

        elif cmd == ControllerCmd.HIDE:
            self.reset()

        self.update()

    def _controller_restr_two_objects(
        self, name, cmd, bindings, get_restr_fun, check_binding_funcs
    ):
        if cmd == ControllerCmd.STEP:
            if len(self._restriction_bindings) == 0:
                binding = find_first(bindings, check_binding_funcs[0])
                if binding:
                    self._restriction_bindings.append(binding)
                    getattr(self, f'checkbox_restr_{name}_1').toggle()
            elif len(self._restriction_bindings) == 1:
                binding = find_first(bindings, check_binding_funcs[0])
                if binding:
                    self._restriction_bindings.append(binding)
                    getattr(self, f'checkbox_restr_{name}_2').toggle()

        elif cmd == ControllerCmd.SUBMIT:
            if len(self._restriction_bindings) != 2:
                raise RuntimeError
            b1, b2 = self._restriction_bindings
            f1_name = b1.get_object_names()[0]
            f2_name = b2.get_object_names()[0]
            restr = get_restr_fun(b1, b2)
            try:
                self._project.add_restriction(restr, (f1_name, f2_name))
            except CannotSolveSystemError:
                pass
            self.reset()
            self._update_list_view()

            controller_name = f'controller_restr_{name}'
            getattr(self, controller_name)(ControllerCmd.SHOW)

        elif cmd == ControllerCmd.SHOW:
            self._reset_behind_statuses()
            status = getattr(ControllerSt, f'restr_{name}'.upper())
            widget = getattr(self, f'widget_restr_{name}')
            widget.show()
            button = getattr(self, f'button_restr_{name}')
            button.setChecked(True)
            self.controller_st = status

        elif cmd == ControllerCmd.HIDE:
            self.reset()

        self.update()

    # ====================================== Events ========================
    def paintEvent(self, event):
        # self._logger.info('paintEvent')

        self._update_current_bindings()

        selected_figures = []
        if self._selected_figure_name is not None:
            selected_figures.append(
                self._project.figures[self._selected_figure_name]
            )
        selected_figures.extend(self._highlighted_figures)

        self.paint_all(
            event,
            self._current_bindings,
            self._project.figures,
            selected_figures,
            self._created_figure,
        )

        self._update_list_view()

    def mousePressEvent(self, event):
        self._logger.debug('mousePressEvent: start')
        if event.button() == Qt.LeftButton:
            x, y = self._to_real_xy(event.x(), event.y())

            if self.controller_st == ControllerSt.ADD_POINT:
                if self.creation_st == CreationSt.POINT_SET:
                    self.controller_add_point(ControllerCmd.SUBMIT)

            elif self.controller_st == ControllerSt.ADD_SEGMENT:
                if self.creation_st == CreationSt.SEGMENT_START_SET:
                    self._created_figure.set_param('x1', x).set_param('y1', y)
                    self.creation_st = CreationSt.SEGMENT_END_SET
                    self.field_x2_add_segment.setFocus()
                    self.field_x2_add_segment.selectAll()
                elif self.creation_st == CreationSt.SEGMENT_END_SET:
                    self.controller_add_segment(ControllerCmd.SUBMIT)

            elif ControllerSt.is_restr(self.controller_st):
                # Make restriction step
                bindings = choose_best_bindings(self._project.bindings, x, y)
                for name in dir(ControllerSt):
                    if (
                        re.match(r'^RESTR_', name)
                        and getattr(ControllerSt, name) == self.controller_st
                    ):
                        controller = getattr(
                            self, f'controller_{name.lower()}'
                        )
                        controller(ControllerCmd.STEP, bindings)

            else:  # self.controller_st == ControllerSt.NOTHING:
                bindings = choose_best_bindings(self._project.bindings, x, y)
                if len(bindings) > 0:
                    if self.action_st == ActionSt.NOTHING:
                        self._moved_binding = bindings[0]
                        self.action_st = ActionSt.BINDING_PRESSED
                    if self.action_st == ActionSt.SELECTED:
                        self._moved_binding = bindings[0]
                        self.action_st = (
                            ActionSt.BINDING_PRESSED_WHILE_SELECTED
                        )
                else:
                    self.reset()

        self.update()

    def mouseMoveEvent(self, event):
        # self._logger.debug('mouseMoveEvent: start')
        x, y = self._to_real_xy(event.x(), event.y())
        self._mouse_xy = (x, y)

        if self.action_st == ActionSt.BINDING_PRESSED:
            self.action_st = ActionSt.MOVE

        elif self.action_st == ActionSt.BINDING_PRESSED_WHILE_SELECTED:
            self.action_st = ActionSt.MOVE_WHILE_SELECTED

        if (
            self.action_st == ActionSt.MOVE
            or self.action_st == ActionSt.MOVE_WHILE_SELECTED
            and self._moved_binding.get_object_names()[0]
            == self._selected_figure_name
        ):

            try:
                self._project.move_figure(self._moved_binding, x, y)
                self._update_fields()
            except CannotSolveSystemError:
                self._project.rollback()

        if self.controller_st == ControllerSt.ADD_POINT:
            if self.creation_st == CreationSt.POINT_SET:
                self._created_figure.set_param('x', x).set_param('y', y)
                self._update_fields()

        elif self.controller_st == ControllerSt.ADD_SEGMENT:
            if self.creation_st == CreationSt.SEGMENT_START_SET:
                self._created_figure.set_param('x1', x).set_param('y1', y)
                self._update_fields()
            elif self.creation_st == CreationSt.SEGMENT_END_SET:
                self._created_figure.set_param('x2', x).set_param('y2', y)
                self._update_fields()

        self.update()

    def mouseReleaseEvent(self, event):
        self._logger.debug('mouseReleaseEvent: start')
        if event.button() == Qt.LeftButton:

            if self.action_st == ActionSt.MOVE:
                self._project.commit()
                self.action_st = ActionSt.NOTHING

            elif self.action_st == ActionSt.MOVE_WHILE_SELECTED:
                self._project.commit()
                self.action_st = ActionSt.SELECTED

            elif (
                self.action_st == ActionSt.BINDING_PRESSED
                or self.action_st == ActionSt.BINDING_PRESSED_WHILE_SELECTED
            ):
                selected_figures = self._moved_binding.get_object_names()
                self._moved_binding = None
                if len(selected_figures) == 1:
                    self._selected_figure_name = selected_figures[0]
                    # Also start changing and set action_st = SELECTED
                    self.select_element_on_tree()
                self.action_st = ActionSt.SELECTED

        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            if self.controller_st == ControllerSt.ADD_POINT:
                self.controller_add_point(ControllerCmd.SUBMIT)
            elif self.controller_st == ControllerSt.ADD_SEGMENT:
                self.controller_add_segment(ControllerCmd.SUBMIT)
            elif ControllerSt.is_restr(self.controller_st):
                name = None
                for name in dir(ControllerSt):
                    if (
                        re.match('^RESTR_', name)
                        and getattr(ControllerSt, name) == self.controller_st
                    ):
                        break
                if name:
                    controller_name = f'controller_{name.lower()}'
                    getattr(self, controller_name)(ControllerCmd.SUBMIT)
        elif key == Qt.Key_Escape:
            self.reset()
        elif modifiers & Qt.ControlModifier:
            if event.key() == Qt.Key_Y:
                self.delete()

    def _reset_footer_widgets(self):
        for w_name, widget in self._footer_widgets.items():
            widget.hide()

        for box in self._footer_checkboxes.values():
            if box.checkState() == Qt.Checked:
                box.toggle()

        for field in self._footer_fields.values():
            field.setValue(0)

    def _uncheck_left_buttons(self):
        for _, button in self._left_buttons.items():
            button.setChecked(False)

    def delete(self, _=None):
        self._logger.debug('delete: start')
        if self._selected_restriction_name is not None:
            self._project.remove_restriction(self._selected_restriction_name)
            self.reset()

        elif self._selected_figure_name is not None:
            self._project.remove_figure(self._selected_figure_name)
            self.reset()

        self.update()

    def new(self, _=None):
        self.reset()
        self._project = CADProject()
        self._filename = None
        self.update()

    def exit(self, _=None):
        self._window.close()

    def reset(self, _=None):
        self._logger.debug('reset: start')
        self._reset_behind_statuses()
        self._reset_statuses()
        self.update()

    def _reset_behind_statuses(self):
        self._selected_figure_name = None  # Name of figure that selected now
        self._selected_restriction_name = None
        self._created_figure = None  # Figure that is created at this moment
        self._highlighted_figures = []
        self._moved_binding = None  # Binding used to move figure
        self._restriction_bindings = []  # Selected bindings for restriction
        self._filename = None

        self._reset_footer_widgets()
        self._uncheck_left_buttons()

    def _reset_statuses(self):
        self.controller_st = ControllerSt.NOTHING
        self.creation_st = CreationSt.NOTHING
        self.action_st = ActionSt.NOTHING

    def save(self, _=None):
        if self._filename is None:
            self.save_as()
        else:
            self._project.save(self._filename)

    def save_as(self, _=None):
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить', '', 'SCAD Files (*.scad)'
        )
        if filename:
            self._filename = filename
            self.save()

    def open(self, _=None):
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Открыть', '', 'SCAD Files (*.scad)'
        )
        if filename:
            self._filename = filename
            self._project.load(self._filename)
        self.update()

    def undo(self, ev):
        self._logger.debug(f'Undo: ev = {ev}')
        try:
            self._project.undo()
        except ActionImpossible:
            pass
        self.update()

    def redo(self, ev):
        self._logger.debug(f'Redo: ev = {ev}')
        try:
            self._project.redo()
        except ActionImpossible:
            pass
        self.update()

    def _update_list_view(self):
        updateble_types = [
            [self.widget_elements_table_figures, self._project.figures],
            [
                self.widget_elements_table_restrictions,
                self._project.restrictions,
            ],
        ]

        for updateble_type_tree, updateble_type in updateble_types:
            for i in reversed(range(updateble_type_tree.childCount())):
                updateble_type_tree.removeChild(updateble_type_tree.child(i))

            for name in updateble_type.keys():
                element = QTreeWidgetItem([name])
                updateble_type_tree.addChild(element)

    def _update_current_bindings(self):
        # Work with bindings
        if self.controller_st == ControllerSt.RESTR_JOINT:
            allowed_bindings_types = (PointBinding, SegmentSpotBinding)
            # TODO: check all variants
        else:
            allowed_bindings_types = None

        x, y = self._mouse_xy
        best_bindings = choose_best_bindings(self._project.bindings, x, y)
        self._current_bindings = []
        for binding in best_bindings:
            if allowed_bindings_types is None or isinstance(
                binding, allowed_bindings_types
            ):
                self._current_bindings.append(binding)

    def paint_all(
        self,
        event: QPaintEvent,
        bindings,
        figures: Dict[str, Figure],
        selected_figures: list,
        created_figure: Optional[Figure] = None,
    ):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255)))
        painter.save()
        painter.translate(*self._center)

        # Paint all
        paint.write_coordinates_near_pointer(painter, self._mouse_xy)

        for figure in figures.values():
            paint.paint_figure(painter, figure, 'basic')

        paint.paint_bindings(painter, figures, bindings)

        # Paint painted figure
        if created_figure is not None:
            paint.paint_figure(painter, created_figure, 'created')

        # Paint selected figure
        for selected_figure in selected_figures:
            paint.paint_figure(painter, selected_figure, 'selected')

        # Finish painting
        painter.restore()
        painter.end()
