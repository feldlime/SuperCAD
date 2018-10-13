import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore

import design  # Это наш конвертированный файл дизайна


class MainWindow(QtWidgets.QMainWindow, design.Ui_SuperCAD):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

    def mouseMoveEvent(self, e):
        # self.setupUi(self) # Если это разкоментить, то координаты будут выводиться в статус бар
        x = e.x()
        y = e.y()
        text = "x: {0},  y: {1}".format(x, y)
        # self.statusbar.showMessage(text)  # Если это разкоментить, то координаты будут выводиться в статус бар
        print(text)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
