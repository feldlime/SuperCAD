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
        timer.start(1)


def main():
    logfile_name = f'log.log'
    # logfile_format = '[%(asctime)s] %(name)-20s %(levelname)-8s %(message)s'
    logfile_format = '%(name)-20s %(levelname)-8s %(message)s'
    logging.basicConfig(
        format=logfile_format,
        level=logging.DEBUG,
        handlers=[logging.FileHandler(logfile_name, 'w', 'utf-8')]
    )

    logging.info('Start working')

    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp

    window.show()  # Показываем окно

    sys.exit(app.exec_())  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
