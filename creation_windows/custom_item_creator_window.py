from creation_windows.creation_window import CreationWindow
from PyQt5.QtWidgets import QWidget, QScrollArea, QLabel
from form import QFormList, QCustomComboBox, QForm


class CustomItemCreatorWindow(CreationWindow):
    def __init__(self, title, w, h, x, y, current_project):
        super().__init__(title, w, h, x, y, current_project)

    def initialize_form(self):
        super().initialize_form()

        form_list = self.form.addWidgetWithField(QFormList(self.generate_form, "Add Field", "Remove Field"), "fields")
        form_list.setMinimumHeight(200)
    
    def initialize_layout(self):
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.form)
        self.setCentralWidget(scrollArea)

    def generate_form(self):
        fieldForm = QForm(lambda x: x)
        fieldForm.addRow("Field Name:", "fieldName")
        fieldForm.addWidgetWithField(QCustomComboBox(
            "Field Type:", 
            ["Integer", "String", "Float", "Double", "Boolean"]
        ), "fieldType").combobox.setEditable(True)
        return fieldForm
