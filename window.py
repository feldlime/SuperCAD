"""Module with main class of application that manage system and picture."""
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

from glwidget import GLWidget
from painter import Painter
from design_setup import UiAddDesign


class MainWindow(QtWidgets.QMainWindow, UiAddDesign):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.setup_ui(self)  # design init

        painter = Painter()
        open_gl = GLWidget(painter, self)

        timer = QTimer(self)
        timer.timeout.connect(open_gl.animate)
        timer.start(1)
