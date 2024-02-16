from creation_windows.creation_window import CreationWindow
from form import QFilePathBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QLabel, QPushButton, QWidget
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
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
                f.write(json.dumps(data))
        
        for key, checkbox in self.checkboxes.items():
            if checkbox.checkState() == 2:
                content = None
                with open(os.path.join(current_project, "item_groups", key), "r") as f:
                    content = json.loads(f.read())

                with open(os.path.join(current_project, "item_groups", key), "w") as f:
                    content["items"].append(os.path.join(current_project, "items", values["id"]+".json"))
                    f.write(json.dumps(content))
        
        super().handle_creation(form)


    def initialize_form(self):
        super().initialize_form()

        nameLineEdit = self.form.addRow("Item Name:", "name")
        idLineEdit = self.form.addRow("Custom ID:", "id")
        imagePickerWidget = self.form.addWidgetRow("Item Texture:", QFilePathBox("Choose Texture", "icons/folder.png", lambda x: x, "Images (*.png)", False), "texturePath")
        self.form.addSubmitButtonRow("Create Item")

        nameLineEdit.textChanged.connect(lambda: idLineEdit.setText(CreationWindow.get_valid_id(nameLineEdit)))
        imagePickerWidget.getLineEdit().textChanged.connect(lambda: imagePickerWidget.setIcon(imagePickerWidget.text()))

        idValidator = QRegExpValidator(QRegExp("[a-z_]+"))
        self.form.addValidator(idValidator, idLineEdit)
    
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
