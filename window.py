"""Module with main class of application (or window?) that manage
 system and picture.
 """

from PyQt5 import QtWidgets
import design
from project import CADProject


class CADWindow(QtWidgets.QMainWindow, design.UiSuperCAD):
    def __init__(self):
        super().__init__()
        self._project = CADProject()

    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError
