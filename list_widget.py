from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QLabel, QSizePolicy, QHBoxLayout, QFormLayout, QScrollArea
from PyQt5.QtCore import Qt


class QListWidget(QWidget):
    def __init__(self, values, handle_click = lambda x: x, *args, **kwargs):
        super(QListWidget, self).__init__(*args, **kwargs)

        self.values = values
        self.layout = QFormLayout()
        self.handle_click = handle_click

        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)

        self.scrollArea = QScrollArea()
        self.scrollContent = QWidget()
        self.scrollContent.setLayout(self.layout)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollContent)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollContent.setObjectName("scroll")

        self.mainLayout.addWidget(self.scrollArea)

        self.buttons = {}

        self.setup()


    def setup(self):
        for key, value in self.values.items():
            widget = QPushButton()
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            widget.setCheckable(True)
            widget.setObjectName("falseButton")

            widget.clicked.connect(self.click)

            layout = QHBoxLayout()
            widget.setLayout(layout)

            label = QLabel(value, self)
            layout.addWidget(label, Qt.AlignmentFlag.AlignLeft)

            self.layout.addWidget(widget)
            self.buttons[widget] = key

    def click(self):
        for button, button_id in self.buttons.items():
            if button.isChecked():
                button.setChecked(False)
                self.handle_click(button_id)
                break

    def clear(self):
        while self.layout.rowCount() > 0:
            self.layout.removeRow(0)

    def update_values(self, new):
        self.values = new
        self.clear()
        self.setup()

    def text(self):
        return list(self.values.values())
