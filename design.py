# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window3.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SuperCAD(object):
    def setupUi(self, SuperCAD):
        SuperCAD.setObjectName("SuperCAD")
        SuperCAD.resize(1280, 650)
        SuperCAD.setMinimumSize(QtCore.QSize(1280, 650))
        SuperCAD.setMaximumSize(QtCore.QSize(1280, 650))
        SuperCAD.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        SuperCAD.setMouseTracking(False)
        SuperCAD.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.centralwidget = QtWidgets.QWidget(SuperCAD)
        self.centralwidget.setObjectName("centralwidget")
        self.work_plane = QtWidgets.QOpenGLWidget(self.centralwidget)
        self.work_plane.setGeometry(QtCore.QRect(50, 0, 1231, 581))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.work_plane.sizePolicy().hasHeightForWidth())
        self.work_plane.setSizePolicy(sizePolicy)
        self.work_plane.setMouseTracking(True)
        self.work_plane.setAutoFillBackground(True)
        self.work_plane.setObjectName("work_plane")
        self.layoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_2.setGeometry(QtCore.QRect(0, 0, 44, 471))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.Instruments = QtWidgets.QVBoxLayout(self.layoutWidget_2)
        self.Instruments.setContentsMargins(0, 0, 0, 0)
        self.Instruments.setSpacing(0)
        self.Instruments.setObjectName("Instruments")
        self.point = QtWidgets.QPushButton(self.layoutWidget_2)
        self.point.setEnabled(True)
        self.point.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/point.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.point.setIcon(icon)
        self.point.setIconSize(QtCore.QSize(30, 30))
        self.point.setCheckable(True)
        self.point.setChecked(False)
        self.point.setAutoRepeat(True)
        self.point.setObjectName("point")
        self.Instruments.addWidget(self.point)
        self.line = QtWidgets.QPushButton(self.layoutWidget_2)
        self.line.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("resources/line.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.line.setIcon(icon1)
        self.line.setIconSize(QtCore.QSize(30, 30))
        self.line.setCheckable(True)
        self.line.setAutoRepeat(True)
        self.line.setObjectName("line")
        self.Instruments.addWidget(self.line)
        self.combine_points = QtWidgets.QPushButton(self.layoutWidget_2)
        self.combine_points.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("resources/combine_points.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.combine_points.setIcon(icon2)
        self.combine_points.setIconSize(QtCore.QSize(30, 30))
        self.combine_points.setCheckable(True)
        self.combine_points.setAutoRepeat(True)
        self.combine_points.setObjectName("combine_points")
        self.Instruments.addWidget(self.combine_points)
        self.point_on_middle_line = QtWidgets.QPushButton(self.layoutWidget_2)
        self.point_on_middle_line.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("resources/point_on_middle_line.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.point_on_middle_line.setIcon(icon3)
        self.point_on_middle_line.setIconSize(QtCore.QSize(30, 30))
        self.point_on_middle_line.setCheckable(True)
        self.point_on_middle_line.setAutoRepeat(True)
        self.point_on_middle_line.setObjectName("point_on_middle_line")
        self.Instruments.addWidget(self.point_on_middle_line)
        self.point_on_line = QtWidgets.QPushButton(self.layoutWidget_2)
        self.point_on_line.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("resources/point_on_line.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.point_on_line.setIcon(icon4)
        self.point_on_line.setIconSize(QtCore.QSize(30, 30))
        self.point_on_line.setCheckable(True)
        self.point_on_line.setAutoRepeat(True)
        self.point_on_line.setObjectName("point_on_line")
        self.Instruments.addWidget(self.point_on_line)
        self.parallelism = QtWidgets.QPushButton(self.layoutWidget_2)
        self.parallelism.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("resources/parallelism.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.parallelism.setIcon(icon5)
        self.parallelism.setIconSize(QtCore.QSize(30, 30))
        self.parallelism.setCheckable(True)
        self.parallelism.setAutoRepeat(True)
        self.parallelism.setObjectName("parallelism")
        self.Instruments.addWidget(self.parallelism)
        self.normal = QtWidgets.QPushButton(self.layoutWidget_2)
        self.normal.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("resources/normal.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.normal.setIcon(icon6)
        self.normal.setIconSize(QtCore.QSize(30, 30))
        self.normal.setCheckable(True)
        self.normal.setAutoRepeat(True)
        self.normal.setObjectName("normal")
        self.Instruments.addWidget(self.normal)
        self.horizontally = QtWidgets.QPushButton(self.layoutWidget_2)
        self.horizontally.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("resources/horizontally.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.horizontally.setIcon(icon7)
        self.horizontally.setIconSize(QtCore.QSize(30, 30))
        self.horizontally.setCheckable(True)
        self.horizontally.setAutoRepeat(True)
        self.horizontally.setObjectName("horizontally")
        self.Instruments.addWidget(self.horizontally)
        self.fix_size = QtWidgets.QPushButton(self.layoutWidget_2)
        self.fix_size.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("resources/fix_size.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fix_size.setIcon(icon8)
        self.fix_size.setIconSize(QtCore.QSize(30, 30))
        self.fix_size.setCheckable(True)
        self.fix_size.setAutoRepeat(True)
        self.fix_size.setObjectName("fix_size")
        self.Instruments.addWidget(self.fix_size)
        self.fix_point = QtWidgets.QPushButton(self.layoutWidget_2)
        self.fix_point.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("resources/fix_point.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fix_point.setIcon(icon9)
        self.fix_point.setIconSize(QtCore.QSize(30, 30))
        self.fix_point.setCheckable(True)
        self.fix_point.setAutoRepeat(True)
        self.fix_point.setObjectName("fix_point")
        self.Instruments.addWidget(self.fix_point)
        self.fix_length = QtWidgets.QPushButton(self.layoutWidget_2)
        self.fix_length.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("resources/fix_length.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fix_length.setIcon(icon10)
        self.fix_length.setIconSize(QtCore.QSize(30, 30))
        self.fix_length.setCheckable(True)
        self.fix_length.setAutoRepeat(True)
        self.fix_length.setObjectName("fix_length")
        self.Instruments.addWidget(self.fix_length)
        self.fix_angle = QtWidgets.QPushButton(self.layoutWidget_2)
        self.fix_angle.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.fix_angle.setText("")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("resources/fix_angle.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fix_angle.setIcon(icon11)
        self.fix_angle.setIconSize(QtCore.QSize(30, 30))
        self.fix_angle.setCheckable(True)
        self.fix_angle.setAutoRepeat(True)
        self.fix_angle.setObjectName("fix_angle")
        self.Instruments.addWidget(self.fix_angle)
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setEnabled(True)
        self.listView.setGeometry(QtCore.QRect(50, 0, 256, 581))
        self.listView.setAutoFillBackground(False)
        self.listView.setObjectName("listView")
        self.Point_widget = QtWidgets.QWidget(self.centralwidget)
        self.Point_widget.setGeometry(QtCore.QRect(50, 580, 281, 31))
        self.Point_widget.setAutoFillBackground(True)
        self.Point_widget.setObjectName("Point_widget")
        self.point_y = QtWidgets.QDoubleSpinBox(self.Point_widget)
        self.point_y.setGeometry(QtCore.QRect(130, 0, 69, 26))
        self.point_y.setObjectName("point_y")
        self.point_x = QtWidgets.QDoubleSpinBox(self.Point_widget)
        self.point_x.setGeometry(QtCore.QRect(30, 0, 69, 26))
        self.point_x.setObjectName("point_x")
        self.label = QtWidgets.QLabel(self.Point_widget)
        self.label.setGeometry(QtCore.QRect(10, -10, 20, 41))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.Point_widget)
        self.label_2.setGeometry(QtCore.QRect(110, -10, 20, 41))
        self.label_2.setObjectName("label_2")
        self.point_submit = QtWidgets.QPushButton(self.Point_widget)
        self.point_submit.setGeometry(QtCore.QRect(210, 0, 61, 25))
        self.point_submit.setObjectName("point_submit")
        self.footer_widget = QtWidgets.QWidget(self.centralwidget)
        self.footer_widget.setGeometry(QtCore.QRect(50, 580, 1231, 31))
        self.footer_widget.setAutoFillBackground(True)
        self.footer_widget.setObjectName("footer_widget")
        self.Line_widget = QtWidgets.QWidget(self.centralwidget)
        self.Line_widget.setGeometry(QtCore.QRect(50, 580, 521, 31))
        self.Line_widget.setAutoFillBackground(True)
        self.Line_widget.setObjectName("Line_widget")
        self.line_y_1 = QtWidgets.QDoubleSpinBox(self.Line_widget)
        self.line_y_1.setGeometry(QtCore.QRect(150, 0, 69, 26))
        self.line_y_1.setObjectName("line_y_1")
        self.line_x_1 = QtWidgets.QDoubleSpinBox(self.Line_widget)
        self.line_x_1.setGeometry(QtCore.QRect(40, 0, 69, 26))
        self.line_x_1.setObjectName("line_x_1")
        self.label_9 = QtWidgets.QLabel(self.Line_widget)
        self.label_9.setGeometry(QtCore.QRect(10, -10, 20, 41))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.Line_widget)
        self.label_10.setGeometry(QtCore.QRect(120, -10, 20, 41))
        self.label_10.setObjectName("label_10")
        self.line_submit = QtWidgets.QPushButton(self.Line_widget)
        self.line_submit.setGeometry(QtCore.QRect(460, 0, 61, 25))
        self.line_submit.setObjectName("line_submit")
        self.label_11 = QtWidgets.QLabel(self.Line_widget)
        self.label_11.setGeometry(QtCore.QRect(230, -10, 20, 41))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.Line_widget)
        self.label_12.setGeometry(QtCore.QRect(340, -10, 20, 41))
        self.label_12.setObjectName("label_12")
        self.line_x_2 = QtWidgets.QDoubleSpinBox(self.Line_widget)
        self.line_x_2.setGeometry(QtCore.QRect(260, 0, 69, 26))
        self.line_x_2.setObjectName("line_x_2")
        self.line_y_2 = QtWidgets.QDoubleSpinBox(self.Line_widget)
        self.line_y_2.setGeometry(QtCore.QRect(370, 0, 69, 26))
        self.line_y_2.setObjectName("line_y_2")
        self.Combine_points_widget = QtWidgets.QWidget(self.centralwidget)
        self.Combine_points_widget.setGeometry(QtCore.QRect(50, 580, 241, 31))
        self.Combine_points_widget.setAutoFillBackground(True)
        self.Combine_points_widget.setObjectName("Combine_points_widget")
        self.combine_points_submit = QtWidgets.QPushButton(self.Combine_points_widget)
        self.combine_points_submit.setGeometry(QtCore.QRect(170, 0, 61, 25))
        self.combine_points_submit.setObjectName("combine_points_submit")
        self.combine_points_point_1 = QtWidgets.QCheckBox(self.Combine_points_widget)
        self.combine_points_point_1.setGeometry(QtCore.QRect(10, 0, 92, 23))
        self.combine_points_point_1.setCheckable(False)
        self.combine_points_point_1.setObjectName("combine_points_point_1")
        self.combine_points_point_2 = QtWidgets.QCheckBox(self.Combine_points_widget)
        self.combine_points_point_2.setGeometry(QtCore.QRect(90, 0, 92, 23))
        self.combine_points_point_2.setCheckable(False)
        self.combine_points_point_2.setObjectName("combine_points_point_2")
        self.Point_on_middle_line_widget = QtWidgets.QWidget(self.centralwidget)
        self.Point_on_middle_line_widget.setGeometry(QtCore.QRect(50, 580, 241, 31))
        self.Point_on_middle_line_widget.setAutoFillBackground(True)
        self.Point_on_middle_line_widget.setObjectName("Point_on_middle_line_widget")
        self.point_on_middle_line_submit = QtWidgets.QPushButton(self.Point_on_middle_line_widget)
        self.point_on_middle_line_submit.setGeometry(QtCore.QRect(170, 0, 61, 25))
        self.point_on_middle_line_submit.setObjectName("point_on_middle_line_submit")
        self.point_on_middle_line_point = QtWidgets.QCheckBox(self.Point_on_middle_line_widget)
        self.point_on_middle_line_point.setGeometry(QtCore.QRect(10, 0, 92, 23))
        self.point_on_middle_line_point.setCheckable(False)
        self.point_on_middle_line_point.setObjectName("point_on_middle_line_point")
        self.point_on_middle_line_line = QtWidgets.QCheckBox(self.Point_on_middle_line_widget)
        self.point_on_middle_line_line.setGeometry(QtCore.QRect(90, 0, 92, 23))
        self.point_on_middle_line_line.setCheckable(False)
        self.point_on_middle_line_line.setObjectName("point_on_middle_line_line")
        self.Point_on_line_widget = QtWidgets.QWidget(self.centralwidget)
        self.Point_on_line_widget.setGeometry(QtCore.QRect(50, 580, 241, 31))
        self.Point_on_line_widget.setAutoFillBackground(True)
        self.Point_on_line_widget.setObjectName("Point_on_line_widget")
        self.point_on_line_submit = QtWidgets.QPushButton(self.Point_on_line_widget)
        self.point_on_line_submit.setGeometry(QtCore.QRect(170, 0, 61, 25))
        self.point_on_line_submit.setObjectName("point_on_line_submit")
        self.point_on_line_point = QtWidgets.QCheckBox(self.Point_on_line_widget)
        self.point_on_line_point.setGeometry(QtCore.QRect(10, 0, 92, 23))
        self.point_on_line_point.setCheckable(False)
        self.point_on_line_point.setObjectName("point_on_line_point")
        self.point_on_line_line = QtWidgets.QCheckBox(self.Point_on_line_widget)
        self.point_on_line_line.setGeometry(QtCore.QRect(90, 0, 92, 23))
        self.point_on_line_line.setCheckable(False)
        self.point_on_line_line.setObjectName("point_on_line_line")
        self.Parallelism_widget = QtWidgets.QWidget(self.centralwidget)
        self.Parallelism_widget.setGeometry(QtCore.QRect(50, 580, 241, 31))
        self.Parallelism_widget.setMouseTracking(False)
        self.Parallelism_widget.setAutoFillBackground(True)
        self.Parallelism_widget.setObjectName("Parallelism_widget")
        self.parallelism_submit = QtWidgets.QPushButton(self.Parallelism_widget)
        self.parallelism_submit.setGeometry(QtCore.QRect(170, 0, 61, 25))
        self.parallelism_submit.setObjectName("parallelism_submit")
        self.parallelism_line_1 = QtWidgets.QCheckBox(self.Parallelism_widget)
        self.parallelism_line_1.setGeometry(QtCore.QRect(10, 0, 92, 23))
        self.parallelism_line_1.setMouseTracking(False)
        self.parallelism_line_1.setShortcut("")
        self.parallelism_line_1.setCheckable(False)
        self.parallelism_line_1.setChecked(False)
        self.parallelism_line_1.setAutoRepeat(False)
        self.parallelism_line_1.setAutoExclusive(False)
        self.parallelism_line_1.setObjectName("parallelism_line_1")
        self.parallelism_line_2 = QtWidgets.QCheckBox(self.Parallelism_widget)
        self.parallelism_line_2.setGeometry(QtCore.QRect(90, 0, 92, 23))
        self.parallelism_line_2.setCheckable(False)
        self.parallelism_line_2.setObjectName("parallelism_line_2")
        self.Normal_widget = QtWidgets.QWidget(self.centralwidget)
        self.Normal_widget.setGeometry(QtCore.QRect(50, 580, 241, 31))
        self.Normal_widget.setAutoFillBackground(True)
        self.Normal_widget.setObjectName("Normal_widget")
        self.normal_submit = QtWidgets.QPushButton(self.Normal_widget)
        self.normal_submit.setGeometry(QtCore.QRect(170, 0, 61, 25))
        self.normal_submit.setObjectName("normal_submit")
        self.normal_line_1 = QtWidgets.QCheckBox(self.Normal_widget)
        self.normal_line_1.setGeometry(QtCore.QRect(10, 0, 92, 23))
        self.normal_line_1.setCheckable(False)
        self.normal_line_1.setObjectName("normal_line_1")
        self.normal_line_2 = QtWidgets.QCheckBox(self.Normal_widget)
        self.normal_line_2.setGeometry(QtCore.QRect(90, 0, 92, 23))
        self.normal_line_2.setCheckable(False)
        self.normal_line_2.setObjectName("normal_line_2")
        self.Horizontally_widget = QtWidgets.QWidget(self.centralwidget)
        self.Horizontally_widget.setGeometry(QtCore.QRect(50, 580, 171, 31))
        self.Horizontally_widget.setAutoFillBackground(True)
        self.Horizontally_widget.setObjectName("Horizontally_widget")
        self.horizontally_submit = QtWidgets.QPushButton(self.Horizontally_widget)
        self.horizontally_submit.setGeometry(QtCore.QRect(90, 0, 61, 25))
        self.horizontally_submit.setObjectName("horizontally_submit")
        self.horizontally_line = QtWidgets.QCheckBox(self.Horizontally_widget)
        self.horizontally_line.setGeometry(QtCore.QRect(10, 0, 92, 23))
        self.horizontally_line.setCheckable(False)
        self.horizontally_line.setObjectName("horizontally_line")
        self.Fix_size_widget = QtWidgets.QWidget(self.centralwidget)
        self.Fix_size_widget.setGeometry(QtCore.QRect(50, 580, 281, 31))
        self.Fix_size_widget.setAutoFillBackground(True)
        self.Fix_size_widget.setObjectName("Fix_size_widget")
        self.label_37 = QtWidgets.QLabel(self.Fix_size_widget)
        self.label_37.setGeometry(QtCore.QRect(70, -10, 51, 41))
        self.label_37.setObjectName("label_37")
        self.fix_size_submit = QtWidgets.QPushButton(self.Fix_size_widget)
        self.fix_size_submit.setGeometry(QtCore.QRect(210, 0, 61, 25))
        self.fix_size_submit.setObjectName("fix_size_submit")
        self.fix_size_length = QtWidgets.QDoubleSpinBox(self.Fix_size_widget)
        self.fix_size_length.setGeometry(QtCore.QRect(130, 0, 69, 26))
        self.fix_size_length.setObjectName("fix_size_length")
        self.fix_size_line = QtWidgets.QCheckBox(self.Fix_size_widget)
        self.fix_size_line.setGeometry(QtCore.QRect(10, 0, 51, 23))
        self.fix_size_line.setCheckable(False)
        self.fix_size_line.setObjectName("fix_size_line")
        self.Fix_point_widget = QtWidgets.QWidget(self.centralwidget)
        self.Fix_point_widget.setGeometry(QtCore.QRect(50, 580, 171, 31))
        self.Fix_point_widget.setAutoFillBackground(True)
        self.Fix_point_widget.setObjectName("Fix_point_widget")
        self.fix_point_submit = QtWidgets.QPushButton(self.Fix_point_widget)
        self.fix_point_submit.setGeometry(QtCore.QRect(90, 0, 61, 25))
        self.fix_point_submit.setObjectName("fix_point_submit")
        self.fix_point_point = QtWidgets.QCheckBox(self.Fix_point_widget)
        self.fix_point_point.setGeometry(QtCore.QRect(10, 0, 92, 23))
        self.fix_point_point.setCheckable(False)
        self.fix_point_point.setObjectName("fix_point_point")
        self.Fix_length_widget = QtWidgets.QWidget(self.centralwidget)
        self.Fix_length_widget.setGeometry(QtCore.QRect(50, 580, 171, 31))
        self.Fix_length_widget.setAutoFillBackground(True)
        self.Fix_length_widget.setObjectName("Fix_length_widget")
        self.fix_length_submit = QtWidgets.QPushButton(self.Fix_length_widget)
        self.fix_length_submit.setGeometry(QtCore.QRect(90, 0, 61, 25))
        self.fix_length_submit.setObjectName("fix_length_submit")
        self.fix_length_line = QtWidgets.QCheckBox(self.Fix_length_widget)
        self.fix_length_line.setGeometry(QtCore.QRect(10, 0, 61, 23))
        self.fix_length_line.setCheckable(False)
        self.fix_length_line.setObjectName("fix_length_line")
        self.Fix_angle_widget = QtWidgets.QWidget(self.centralwidget)
        self.Fix_angle_widget.setGeometry(QtCore.QRect(50, 580, 241, 31))
        self.Fix_angle_widget.setAutoFillBackground(True)
        self.Fix_angle_widget.setObjectName("Fix_angle_widget")
        self.fix_angle_submit = QtWidgets.QPushButton(self.Fix_angle_widget)
        self.fix_angle_submit.setGeometry(QtCore.QRect(170, 0, 61, 25))
        self.fix_angle_submit.setObjectName("fix_angle_submit")
        self.fix_angle_line_1 = QtWidgets.QCheckBox(self.Fix_angle_widget)
        self.fix_angle_line_1.setGeometry(QtCore.QRect(10, 0, 92, 23))
        self.fix_angle_line_1.setCheckable(False)
        self.fix_angle_line_1.setObjectName("fix_angle_line_1")
        self.fix_angle_line_2 = QtWidgets.QCheckBox(self.Fix_angle_widget)
        self.fix_angle_line_2.setGeometry(QtCore.QRect(90, 0, 92, 23))
        self.fix_angle_line_2.setCheckable(False)
        self.fix_angle_line_2.setObjectName("fix_angle_line_2")
        self.footer_widget.raise_()
        self.work_plane.raise_()
        self.layoutWidget_2.raise_()
        self.listView.raise_()
        self.Point_widget.raise_()
        self.Line_widget.raise_()
        self.Combine_points_widget.raise_()
        self.Point_on_middle_line_widget.raise_()
        self.Point_on_line_widget.raise_()
        self.Parallelism_widget.raise_()
        self.Normal_widget.raise_()
        self.Horizontally_widget.raise_()
        self.Fix_size_widget.raise_()
        self.Fix_point_widget.raise_()
        self.Fix_length_widget.raise_()
        self.Fix_angle_widget.raise_()
        SuperCAD.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SuperCAD)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        SuperCAD.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SuperCAD)
        self.statusbar.setObjectName("statusbar")
        SuperCAD.setStatusBar(self.statusbar)
        self.actionNew = QtWidgets.QAction(SuperCAD)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtWidgets.QAction(SuperCAD)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(SuperCAD)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtWidgets.QAction(SuperCAD)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionClose = QtWidgets.QAction(SuperCAD)
        self.actionClose.setObjectName("actionClose")
        self.actionUndo = QtWidgets.QAction(SuperCAD)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtWidgets.QAction(SuperCAD)
        self.actionRedo.setObjectName("actionRedo")
        self.actionShow_elements_table = QtWidgets.QAction(SuperCAD)
        self.actionShow_elements_table.setCheckable(True)
        self.actionShow_elements_table.setChecked(True)
        self.actionShow_elements_table.setObjectName("actionShow_elements_table")
        self.actionExit = QtWidgets.QAction(SuperCAD)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionExit)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionUndo)
        self.menuMenu.addAction(self.actionRedo)
        self.menuMenu.addAction(self.actionShow_elements_table)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(SuperCAD)
        self.actionShow_elements_table.triggered['bool'].connect(self.listView.hide)
        self.actionExit.changed.connect(SuperCAD.close)
        self.point.clicked['bool'].connect(self.Point_widget.hide)
        self.line.clicked['bool'].connect(self.Line_widget.hide)
        QtCore.QMetaObject.connectSlotsByName(SuperCAD)

        # self.Point_widget.is
    def retranslateUi(self, SuperCAD):
        _translate = QtCore.QCoreApplication.translate
        SuperCAD.setWindowTitle(_translate("SuperCAD", "MainWindow"))
        self.label.setText(_translate("SuperCAD", "X:"))
        self.label_2.setText(_translate("SuperCAD", "Y:"))
        self.point_submit.setText(_translate("SuperCAD", "Submit"))
        self.label_9.setText(_translate("SuperCAD", "X1:"))
        self.label_10.setText(_translate("SuperCAD", "Y1:"))
        self.line_submit.setText(_translate("SuperCAD", "Submit"))
        self.label_11.setText(_translate("SuperCAD", "X2:"))
        self.label_12.setText(_translate("SuperCAD", "Y2:"))
        self.combine_points_submit.setText(_translate("SuperCAD", "Submit"))
        self.combine_points_point_1.setText(_translate("SuperCAD", "Point 1"))
        self.combine_points_point_2.setText(_translate("SuperCAD", "Point 2"))
        self.point_on_middle_line_submit.setText(_translate("SuperCAD", "Submit"))
        self.point_on_middle_line_point.setText(_translate("SuperCAD", "Point"))
        self.point_on_middle_line_line.setText(_translate("SuperCAD", "Line"))
        self.point_on_line_submit.setText(_translate("SuperCAD", "Submit"))
        self.point_on_line_point.setText(_translate("SuperCAD", "Point"))
        self.point_on_line_line.setText(_translate("SuperCAD", "Line"))
        self.parallelism_submit.setText(_translate("SuperCAD", "Submit"))
        self.parallelism_line_1.setText(_translate("SuperCAD", "Line 1"))
        self.parallelism_line_2.setText(_translate("SuperCAD", "Line 2"))
        self.normal_submit.setText(_translate("SuperCAD", "Submit"))
        self.normal_line_1.setText(_translate("SuperCAD", "Line 1"))
        self.normal_line_2.setText(_translate("SuperCAD", "Line 2"))
        self.horizontally_submit.setText(_translate("SuperCAD", "Submit"))
        self.horizontally_line.setText(_translate("SuperCAD", "Line"))
        self.label_37.setText(_translate("SuperCAD", "length:"))
        self.fix_size_submit.setText(_translate("SuperCAD", "Submit"))
        self.fix_size_line.setText(_translate("SuperCAD", "Line"))
        self.fix_point_submit.setText(_translate("SuperCAD", "Submit"))
        self.fix_point_point.setText(_translate("SuperCAD", "Point"))
        self.fix_length_submit.setText(_translate("SuperCAD", "Submit"))
        self.fix_length_line.setText(_translate("SuperCAD", "Line"))
        self.fix_angle_submit.setText(_translate("SuperCAD", "Submit"))
        self.fix_angle_line_1.setText(_translate("SuperCAD", "Line 1"))
        self.fix_angle_line_2.setText(_translate("SuperCAD", "Line 2"))
        self.menuFile.setTitle(_translate("SuperCAD", "File"))
        self.menuMenu.setTitle(_translate("SuperCAD", "Menu"))
        self.actionNew.setText(_translate("SuperCAD", "New"))
        self.actionNew.setShortcut(_translate("SuperCAD", "Ctrl+N"))
        self.actionOpen.setText(_translate("SuperCAD", "Open"))
        self.actionOpen.setShortcut(_translate("SuperCAD", "Ctrl+O"))
        self.actionSave.setText(_translate("SuperCAD", "Save"))
        self.actionSave.setShortcut(_translate("SuperCAD", "Ctrl+S"))
        self.actionSaveAs.setText(_translate("SuperCAD", "Save As"))
        self.actionSaveAs.setShortcut(_translate("SuperCAD", "Ctrl+Shift+S"))
        self.actionClose.setText(_translate("SuperCAD", "Close"))
        self.actionClose.setShortcut(_translate("SuperCAD", "Ctrl+W"))
        self.actionUndo.setText(_translate("SuperCAD", "Undo"))
        self.actionUndo.setShortcut(_translate("SuperCAD", "Ctrl+Z"))
        self.actionRedo.setText(_translate("SuperCAD", "Redo"))
        self.actionRedo.setShortcut(_translate("SuperCAD", "Ctrl+Shift+Z"))
        self.actionShow_elements_table.setText(_translate("SuperCAD", "Show elements table"))
        self.actionShow_elements_table.setShortcut(_translate("SuperCAD", "Ctrl+T"))
        self.actionExit.setText(_translate("SuperCAD", "Exit"))
        self.actionExit.setShortcut(_translate("SuperCAD", "Ctrl+Q"))

