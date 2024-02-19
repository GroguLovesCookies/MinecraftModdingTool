from creation_windows.creation_window import CreationWindow
from form import QForm, QCustomCheckBox, QCustomComboBox, QCustomLineEdit, QFilePathBox
from PyQt5.QtWidgets import QPushButton, QCheckBox, QLabel
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIntValidator, QDoubleValidator
import shutil
import os
import json


class BlockCreatorWindow(CreationWindow):
    def initialize_form(self):
        super().initialize_form()

        modelLabel = QLabel("Block Model")
        modelLabel.setObjectName("itemGroupChoiceHeading")
        self.form.addWidgetWithoutField(modelLabel)
        
        imagePickerWidget = self.form.addWidgetRow("Block Texture:", QFilePathBox("Choose Texture", "icons/folder.png", lambda x: x, "Images (*.png)", False), "texturePath")
        imagePickerWidget.getLineEdit().textChanged.connect(lambda: imagePickerWidget.setIcon(imagePickerWidget.text()))

        settingsLabel = QLabel("Block Settings")
        settingsLabel.setObjectName("itemGroupChoiceHeading")
        self.form.addWidgetWithoutField(settingsLabel)

        subForm = self.form.addWidgetWithField(QForm(lambda x: x), "settings")

        subForm.setStyleSheet("margin-left: 20px; margin-top: 0px;")

        handBreakable = subForm.addWidgetWithField(QCustomCheckBox("Breakable By Hand:"), "handBreakable")
        instamine = subForm.addWidgetWithField(QCustomCheckBox("Is Instaminable:"), "instaminable")
        requiresTool = subForm.addWidgetWithField(QCustomCheckBox("Requires Tool:"), "requiresTool")

        requiredTool = subForm.addWidgetWithField(QCustomComboBox("Required Tool:", ["Pickaxe", "Axe", "Shovel", "Hoe", "Sword"]), "requiredTool")
        requiredTier = subForm.addWidgetWithField(QCustomComboBox("Required Tier:", ["Stone", "Iron", "Diamond", "Netherite"]), "requiredTier")
        lightLevel = subForm.addWidgetWithField(QCustomLineEdit("Light Level:"), "lightLevel")
        lightLevelValidator = QIntValidator(0, 15)
        self.form.addValidator(lightLevelValidator, lightLevel.lineEdit)

        strength = subForm.addRow("Hardness:", "strength")
        strengthValidator = QDoubleValidator(0, 100, 2)
        strength.setValidator(strengthValidator)
        strength.focusOutEvent = lambda e: self.clampValue(0, 100, strength)

        subForm.setValues({"lightLevel": "0", "strength": "20.0"})
        lightLevel.lineEdit.setValidator(lightLevelValidator)
        
        dropsLabel = QLabel("Drops")
        dropsLabel.setObjectName("itemGroupChoiceHeading")
        self.form.addWidgetWithoutField(dropsLabel)
        dropsForm = self.form.addWidgetWithField(QForm(lambda x: x), "drops")
        dropsForm.addWidgetWithField(QCustomComboBox("Drop Type", ["Self", "Ores"]), "dropType")


        self.form.addSubmitButtonRow("Create Block")

    def clampValue(self, low, high, widget):
        try:
            widget.setText(str(min(high, max(low, float(widget.text())))))
        except:
            return

    def initialize_layout(self):
        self.setCentralWidget(self.form)

    def handle_creation(self, form):
        values = form.getValues()
        current_project = values["currentProject"]
        if not os.path.isdir(f"{current_project}/textures"):
            os.mkdir(f"{current_project}/textures")
        if not os.path.isdir(f"{current_project}/blocks"):
            os.mkdir(f"{current_project}/blocks")
        
        if os.path.isfile(values["texturePath"]):
            filename = os.path.split(values["texturePath"])[-1]
            shutil.copy(values["texturePath"], os.path.join(current_project, "textures", filename))
            with open(f"{current_project}/blocks/{values['id']}.json", "w") as f:
                modID = ""
                with open(f"{current_project}/properties.json") as p:
                    modID = json.loads(p.read())["mod_id"]
                data = {"name": values["name"], "id": f"{modID}:{values['id']}", "texture": f"{current_project}/textures/{filename}",
                "properties": values["settings"], "drops": values["drops"]}
                f.write(json.dumps(data))
        
        super().handle_creation(form)

    def setVisibility(self, box, *args):
        for arg in args:
            arg.setVisible(box.isChecked())
        
