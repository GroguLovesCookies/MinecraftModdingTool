from creation_windows.creation_window import CreationWindow
from form import QFilePathBox, QForm, QCustomCheckBox, QFormList
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QLabel, QPushButton, QWidget
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QIntValidator, QDoubleValidator
import os
import json
import shutil


class ItemCreatorWindow(CreationWindow):
    def __init__(self, title, w, h, x, y, current_project):
        self.checkboxes = {}
        self.itemGroupChooseWidget = QWidget()

        super().__init__(title, w, h, x, y, current_project)

    
    def handle_creation(self, form):
        values = form.getValues()
        current_project = values["currentProject"]
        if not os.path.isdir(f"{current_project}/textures"):
            os.mkdir(f"{current_project}/textures")
        if not os.path.isdir(f"{current_project}/items"):
            os.mkdir(f"{current_project}/items")
        
        if os.path.isfile(values["texturePath"]):
            filename = os.path.split(values["texturePath"])[-1]
            shutil.copy(values["texturePath"], os.path.join(current_project, "textures", filename))
            with open(f"{current_project}/items/{values['id']}.json", "w") as f:
                modID = ""
                with open(f"{current_project}/properties.json") as p:
                    modID = json.loads(p.read())["mod_id"]
                data = {"name": values["name"], "id": f"{modID}:{values['id']}", "texture": f"{current_project}/textures/{filename}"}
                if values["isFood"]:
                    data["foodProperties"] = values["foodProperties"]
                f.write(json.dumps(data))
        
        for key, checkbox in self.checkboxes.items():
            if checkbox.checkState() == 2:
                content = None
                with open(os.path.join(current_project, "item_groups", key), "r") as f:
                    content = json.loads(f.read())

                with open(os.path.join(current_project, "item_groups", key), "w") as f:
                    content["items"].append(f"{modID}:{values['id']}")
                    f.write(json.dumps(content))
        
        super().handle_creation(form)


    def initialize_form(self):
        super().initialize_form()
        imagePickerWidget = self.form.addWidgetRow("Item Texture:", QFilePathBox("Choose Texture", "icons/folder.png", lambda x: x, "Images (*.png)", False), "texturePath")
        isFoodCheckBox = self.form.addWidgetWithField(QCustomCheckBox("Is Food:"), "isFood")

        foodForm = self.form.addWidgetWithField(QForm(lambda x: x), "foodProperties")
        foodForm.setVisible(False)  

        foodHeading = QLabel("Food Properties")
        foodHeading.setObjectName("itemGroupChoiceHeading")
        foodForm.addWidgetWithoutField(foodHeading)

        foodHunger = foodForm.addRow("Hunger Restored:", "hunger")
        foodHunger.setValidator(QIntValidator(0, 20))

        foodSaturation = foodForm.addRow("Saturation:", "saturation")
        foodSaturation.setValidator(QDoubleValidator(0, 2, 2))

        alwaysEdible = foodForm.addWidgetWithField(QCustomCheckBox("Can Be Eaten When Full:"), "alwaysEdible")

        statusEffectFormList = foodForm.addWidgetWithField(QFormList(self.generate_form, "Add Status Effect", "Remove"), "statusEffects")
        statusEffectFormList.add_form()
        statusEffectFormList.add_form()

        isFoodCheckBox.checkbox.toggled.connect(lambda: foodForm.setVisible(isFoodCheckBox.checkbox.isChecked()))

        self.form.addSubmitButtonRow("Create Item")

        imagePickerWidget.getLineEdit().textChanged.connect(lambda: imagePickerWidget.setIcon(imagePickerWidget.text()))

    def generate_form(self):
        statusEffectForm = QForm(lambda x: x)
        statusEffect = statusEffectForm.addRow("Status Effect:", "statusEffect")
        statusEffectPower = statusEffectForm.addRow("Multiplier:", "statusEffectMultiplier")
        statusEffectPowerValidator = QIntValidator(1, 255)
        statusEffectPower.setValidator(statusEffectPowerValidator)
        statusEffectDuration = statusEffectForm.addRow("Duration (Ticks):", "duration")
        statusEffectDuration.setValidator(QIntValidator(0, 9999))
        self.form.addValidator(statusEffectPowerValidator, statusEffectPower)
        

        statusEffectChance = statusEffectForm.addRow("Chance:", "statusEffectChance")
        statusEffectChanceValidator = QIntValidator(0, 100)
        statusEffectChance.setValidator(statusEffectChanceValidator)
        self.form.addValidator(statusEffectChanceValidator, statusEffectChance)
        statusEffectForm.setValues({"statusEffectChance": "100"})

        return statusEffectForm
    
    def initialize_layout(self):
        self.mainLayout.addWidget(self.form, 75)
        self.mainLayout.addWidget(self.itemGroupChooseWidget, 25)

    def initialize_extras(self):
        itemGroupChooseLayout = QFormLayout()
        self.itemGroupChooseWidget.setLayout(itemGroupChooseLayout)

        itemGroups = ItemCreatorWindow.get_item_groups(self.current_project)
        if len(itemGroups) == 0:
            label = QLabel("No Item Groups Found")
            label.setObjectName("itemGroupChoiceHeading")
            itemGroupChooseLayout.addWidget(label)
            itemGroupChooseLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            itemGroupChooser = QWidget()
            itemGroupChooserLayout = QFormLayout()
            itemGroupChooser.setLayout(itemGroupChooserLayout)

            heading = QLabel("Add to Item Group")
            heading.setObjectName("itemGroupChoiceHeading")
            itemGroupChooserLayout.addWidget(heading)

            itemGroupChooseLayout.addWidget(itemGroupChooser)

            for key, value in itemGroups.items():
                selectionLayout = QHBoxLayout()
                selectionLayout.addWidget(QLabel(value), 90)
                checkbox = QCheckBox()
                selectionLayout.addWidget(checkbox, 10)
                itemGroupChooserLayout.addRow(selectionLayout)
                self.checkboxes[key] = checkbox

    @staticmethod
    def get_item_groups(current_project):
        item_groups = {}
        if os.path.isdir(f"{current_project}/item_groups"):
            for file in os.listdir(f"{current_project}/item_groups"):
                with open(os.path.join(current_project, "item_groups", file)) as f:
                    item_groups[file] = json.loads(f.read())["name"]
        return item_groups
