from creation_windows.creation_window import CreationWindow
from form import QItemBrowseBox, QCustomCheckBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QIntValidator, QDoubleValidator
import os
import json


class SmeltingCreatorWindow(CreationWindow):
    def handle_creation(self, form):
        values = form.getValues()
        current_project = values["currentProject"]
        if not os.path.isdir(f"{current_project}/smelting"):
            os.mkdir(f"{current_project}/smelting")

        with open(f"{current_project}/smelting/{values['id']}_smelting.json", "w") as f:
            f.write(json.dumps(values))

        super().handle_creation(form)

    def initialize_layout(self):
        self.setCentralWidget(self.form)

    def initialize_form(self):
        super().initialize_form()

        inputItemBrowser = self.form.addWidgetRow("Input Item:", 
        QItemBrowseBox("Select Input Item", "icons/folder.png", lambda x: x, self.current_project),
        "inputItem")

        outputItemBrowser = self.form.addWidgetRow("Output Item:", 
        QItemBrowseBox("Select Output Item", "icons/folder.png", lambda x: x, self.current_project),
        "outputItem")

        smeltTimeLineEdit = self.form.addRow("Smelt Time (Ticks):", "smeltTime")
        smeltTimeSeconds = self.form.addLabelRow("Smelt Time (Seconds):", "", "smeltTimeSeconds")
        smeltTimeLineEdit.textChanged.connect(lambda: self.setSmeltSeconds(smeltTimeLineEdit, smeltTimeSeconds))

        smeltTimeValidator = QIntValidator(0, 9999)
        smeltTimeLineEdit.setValidator(smeltTimeValidator)
        self.form.addValidator(smeltTimeValidator, smeltTimeLineEdit)

        experienceLineEdit = self.form.addRow("Experience:", "experience")
        experienceValidator = QDoubleValidator(0.00, 999.99, 2)
        experienceLineEdit.setValidator(experienceValidator)

        addBlasting = self.form.addWidgetWithField(QCustomCheckBox("Add Blasting:"), "addBlasting")
        addSmoking = self.form.addWidgetWithField(QCustomCheckBox("Add Smoking:"), "addSmoking")

        self.form.setValues({"smeltTime": "200"})
        self.form.addSubmitButtonRow("Create")

    def setSmeltSeconds(self, smeltLineEdit, smeltSeconds):
        if smeltLineEdit.text() == "":
            return
        else:
            smeltSeconds.setText(str(int(smeltLineEdit.text())/20)+"s")

    def clampExperience(self, experienceLineEdit):
        if "." not in experienceLineEdit.text():
            return
        diff = len(experienceLineEdit.text().split(".")[1]) - 2
        if diff > 0:
            experienceLineEdit.setText(experienceLineEdit.text()[:len(experienceLineEdit.text())-diff])