from PyQt5.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton
from form import QForm, QFilePathBox


class CreationWindow(QMainWindow):
    onDestroy = None

    def __init__(self, title, w, h, x, y, current_project):
        super().__init__()

        self.setWindowTitle(title)
        self.resize(w, h)
        self.move(x, y)
        self.current_project = current_project

        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)

        self.form = QForm(self.handle_creation)
        self.initialize_layout()
        self.initialize_form()
        self.initialize_extras()



    def initialize_form(self):
        self.form.addHiddenInput("currentProject")
        self.form.setValues({"currentProject": self.current_project})

    def initialize_layout(self):
        ...

    def initialize_extras(self):
        ...

    def handle_creation(self, form):
        CreationWindow.onDestroy()
        self.destroy()

    @staticmethod
    def get_valid_id(inputLineEdit):
        text = inputLineEdit.text()
        return "_".join(text.lower().split())

