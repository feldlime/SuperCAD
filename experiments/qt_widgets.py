import sys

import PyQt5 as qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# Hello world
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Hello")
        layout = QGridLayout()
        self.setLayout(layout)
        label = QLabel("Hello, World!")
        layout.addWidget(label, 0, 0)


# Window
class Window(QWindow):
    def __init__(self):
        QWindow.__init__(self)
        self.setTitle("Window")
        self.resize(400, 300)


# Box layout
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.setLayout(layout)
        label = QLabel("Label 1")
        layout.addWidget(label, 0)
        label = QLabel("Label 2")
        layout.addWidget(label, 0)
        layout2 = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addLayout(layout2)
        label = QLabel("Label 3")
        layout2.addWidget(label, 0)
        label = QLabel("Label 4")
        layout2.addWidget(label, 0)


# Grid layout
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        label = QLabel("Label (0, 0)")
        layout.addWidget(label, 0, 0)
        label = QLabel("Label (0, 1)")
        layout.addWidget(label, 0, 1)
        label = QLabel("Label (1, 0) spanning 2 columns")
        layout.addWidget(label, 1, 0, 1, 2)
        label = QLabel("Label (1, 0) spanning 2 rows")
        layout.addWidget(label, 0, 2, 2, 1)


# Label
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        label = QLabel("The Story of Dale")
        layout.addWidget(label, 0, 0)
        label = QLabel(
            "Few people could understand Dale's motivation. "
            "It wasn't something that was easy to appreciate without "
            "the full context, but the full context was lost on Dale "
            "as he struggled with what he had done.")
        label.setWordWrap(True)
        layout.addWidget(label, 0, 1)


# Push button
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        button = QPushButton("Click Me")
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button, 0, 0)

    def on_button_clicked(self):
        print("The button was pressed!")


# Radio button
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        radiobutton = QRadioButton("Brazil")
        radiobutton.setChecked(True)
        radiobutton.country = "Brazil"
        radiobutton.toggled.connect(self.on_radio_button_toggled)
        layout.addWidget(radiobutton, 0, 0)
        radiobutton = QRadioButton("Argentina")
        radiobutton.country = "Argentina"
        radiobutton.toggled.connect(self.on_radio_button_toggled)
        layout.addWidget(radiobutton, 0, 1)
        radiobutton = QRadioButton("Ecuador")
        radiobutton.country = "Ecuador"
        radiobutton.toggled.connect(self.on_radio_button_toggled)
        layout.addWidget(radiobutton, 0, 2)

    def on_radio_button_toggled(self):
        radiobutton = self.sender()
        if radiobutton.isChecked():
            print("Selected country is %s" % (radiobutton.country))


# Checkbox
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.checkbox1 = QCheckBox("Kestrel")
        self.checkbox1.setChecked(True)
        self.checkbox1.toggled.connect(self.checkbox_toggled)
        layout.addWidget(self.checkbox1, 0, 0)
        self.checkbox2 = QCheckBox("Sparrowhawk")
        self.checkbox2.toggled.connect(self.checkbox_toggled)
        layout.addWidget(self.checkbox2, 1, 0)
        self.checkbox3 = QCheckBox("Hobby")
        self.checkbox3.toggled.connect(self.checkbox_toggled)
        layout.addWidget(self.checkbox3, 2, 0)

    def checkbox_toggled(self):
        selected = []
        if self.checkbox1.isChecked():
            selected.append("Kestrel")
        if self.checkbox2.isChecked():
            selected.append("Sparrowhawk")
        if self.checkbox3.isChecked():
            selected.append("Hobby")
        print("Selected: %s" % (" ".join(selected)))


# Tooltip
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        button = QPushButton("Simple ToolTip")
        button.setToolTip("This ToolTip simply displays text.")
        layout.addWidget(button, 0, 0)
        button = QPushButton("Formatted ToolTip")
        button.setToolTip("<b>Formatted text</b> can also be displayed.")
        layout.addWidget(button, 1, 0)


# Whatsthis
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        label = QLabel("Focus ComboBox and press SHIFT+F1")
        layout.addWidget(label)
        self.combobox = QComboBox()
        self.combobox.setWhatsThis("This is a 'WhatsThis' object description.")
        layout.addWidget(self.combobox)


# Line edit
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.lineedit = QLineEdit()
        self.lineedit.returnPressed.connect(self.return_pressed)
        layout.addWidget(self.lineedit, 0, 0)

    def return_pressed(self):
        print(self.lineedit.text())


# Button group
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.buttongroup = QButtonGroup()
        self.buttongroup.setExclusive(False)
        self.buttongroup.buttonClicked[int].connect(self.on_button_clicked)
        button = QPushButton("Button 1")
        self.buttongroup.addButton(button, 1)
        layout.addWidget(button)
        button = QPushButton("Button 2")
        self.buttongroup.addButton(button, 2)
        layout.addWidget(button)

    def on_button_clicked(self, id):
        for button in self.buttongroup.buttons():
            if button is self.buttongroup.button(id):
                print("%s was clicked!" % (button.text()))


# Group box
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("GroupBox")
        layout = QGridLayout()
        self.setLayout(layout)
        groupbox = QGroupBox("GroupBox Example")
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        vbox = QVBoxLayout()
        groupbox.setLayout(vbox)
        radiobutton = QRadioButton("RadioButton 1")
        radiobutton.setChecked(True)
        vbox.addWidget(radiobutton)
        radiobutton = QRadioButton("RadioButton 2")
        vbox.addWidget(radiobutton)


# Size grip (no example)


# Splitter (no example)


# Frame (no example)


# Slider
class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        slider = QSlider(Qt.Horizontal)
        slider.setValue(4)
        layout.addWidget(slider, 0, 0)
        slider = QSlider(Qt.Vertical)
        slider.setValue(4)
        layout.addWidget(slider, 0, 1)


# Scroll bar

app = QApplication(sys.argv)
screen = Window()
screen.show()
sys.exit(app.exec_())
