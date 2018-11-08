from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

import design
from GLWidget import GLWidget
from Painter import Painter


class MainWindow(QtWidgets.QMainWindow, design.Ui_SuperCAD):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super(MainWindow, self).__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # Дописываем design под себя
        self.listView.hide()
        self.hide_all_footer_widgets()
        self.actionShow_elements_table.triggered['bool'].connect(
            self.triggered_list_view)
        self.point.clicked['bool'].connect(self.triggered_point_widget)
        self.line.clicked['bool'].connect(self.triggered_line_widget)
        self.combine_points.clicked['bool'].connect(
            self.triggered_combine_points_widget)
        self.point_on_middle_line.clicked['bool'].connect(
            self.triggered_point_on_middle_line_widget)
        self.point_on_line.clicked['bool'].connect(
            self.triggered_point_on_line_widget)
        self.parallelism.clicked['bool'].connect(
            self.triggered_parallelism_widget)
        self.normal.clicked['bool'].connect(self.triggered_normal_widget)
        self.horizontally.clicked['bool'].connect(
            self.triggered_horizontally_widget)
        self.fix_size.clicked['bool'].connect(self.triggered_fix_size_widget)
        self.fix_point.clicked['bool'].connect(self.triggered_fix_point_widget)
        self.fix_length.clicked['bool'].connect(
            self.triggered_fix_length_widget)
        self.fix_angle.clicked['bool'].connect(self.triggered_fix_angle_widget)

        helper = Painter()
        openGL = GLWidget(helper, self)

        timer = QTimer(self)
        timer.timeout.connect(openGL.animate)
        timer.start(1)

    def triggered_list_view(self, change):
        if change:
            self.listView.show()
        else:
            self.listView.hide()

    def triggered_point_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Point')
            self.Point_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Point_widget.hide()

    def triggered_line_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Line')
            self.Line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Line_widget.hide()

    def triggered_combine_points_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose first point to combine')
            self.Combine_points_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Combine_points_widget.hide()

    def triggered_point_on_middle_line_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage(
                'Choose line to combine with middle of line')
            self.Point_on_middle_line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Point_on_middle_line_widget.hide()

    def triggered_point_on_line_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose line to combine with line')
            self.Point_on_line_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Point_on_line_widget.hide()

    def triggered_parallelism_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose changeable line')
            self.Parallelism_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Parallelism_widget.hide()

    def triggered_normal_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose changeable line')
            self.Normal_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Normal_widget.hide()

    def triggered_horizontally_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose changeable line')
            self.Horizontally_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Horizontally_widget.hide()

    def triggered_fix_size_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose line for fix size')
            self.Fix_size_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Fix_size_widget.hide()

    def triggered_fix_point_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose point for fix')
            self.Fix_point_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Fix_point_widget.hide()

    def triggered_fix_length_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose point for fix length')
            self.Fix_length_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Fix_length_widget.hide()

    def triggered_fix_angle_widget(self, change):
        self.hide_all_footer_widgets()
        if change:
            self.statusbar.showMessage('Choose first line for fix angle')
            self.Fix_angle_widget.show()
        else:
            self.statusbar.showMessage('')
            self.Fix_angle_widget.hide()

    def hide_all_footer_widgets(self):
        self.Line_widget.hide()
        self.Point_widget.hide()
        self.Combine_points_widget.hide()
        self.Point_on_middle_line_widget.hide()
        self.Point_on_line_widget.hide()
        self.Parallelism_widget.hide()
        self.Normal_widget.hide()
        self.Horizontally_widget.hide()
        self.Fix_size_widget.hide()
        self.Fix_point_widget.hide()
        self.Fix_length_widget.hide()
        self.Fix_angle_widget.hide()

        self.point.setChecked(False)
        self.line.setChecked(False)
        self.combine_points.setChecked(False)
        self.point_on_middle_line.setChecked(False)
        self.point_on_line.setChecked(False)
        self.parallelism.setChecked(False)
        self.normal.setChecked(False)
        self.horizontally.setChecked(False)
        self.fix_size.setChecked(False)
        self.fix_point.setChecked(False)
        self.fix_length.setChecked(False)
        self.fix_angle.setChecked(False)
