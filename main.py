"""Main module that creates and closes application."""
import sys
import logging

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow

from window import WindowContent
import diagnostic_context


class MainWindow(QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()

        self._content = WindowContent(self)
        self._content.update()

    def keyPressEvent(self, event):
        self._content.keyPressEvent(event)


def main():
    diagnostic_context.VERBOSE = True

    # logfile_name = f'log.log'
    logfile_format = '[%(asctime)s] %(name)-20s %(levelname)-8s %(message)s'
    logging.basicConfig(
        format=logfile_format,
        level=logging.INFO,
        # handlers=[logging.FileHandler(logfile_name, 'w', 'utf-8')]
    )

    logging.info('Start working')

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
