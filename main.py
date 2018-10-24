"""Main module that creates and closes application."""


import sys
from window import CADWindow
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = CADWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
