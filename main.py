"""Main module that creates and closes application."""


import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow
import logging

from window import WindowContent


class MainWindow(QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()

        self._content = WindowContent(self)

        timer = QTimer(self)
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(self._content.animate)
        timer.start(50)

    def keyPressEvent(self, event):
        self._content.keyPressEvent(event)


def main():
    logfile_name = f'log.log'
    # logfile_format = '[%(asctime)s] %(name)-20s %(levelname)-8s %(message)s'
    logfile_format = '%(name)-20s %(levelname)-8s %(message)s'
    logging.basicConfig(
        format=logfile_format,
        level=logging.DEBUG,
        # handlers=[logging.FileHandler(logfile_name, 'w', 'utf-8')]
    )

    logging.info('Start working')

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
