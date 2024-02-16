import os
import json
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QLabel, QLineEdit, QWidget, QSizePolicy, QCheckBox
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QPixmap
from form import QForm, QFilePathBox, QItemBrowseBox
import shutil
from item_browser import QItemSelectorWindow
from creation_windows.item_group_creator_window import ItemGroupCreatorWindow


def create_new_item_group(menuWindow, current_project):
    menuWindow.hide()
    return initialize_item_group_creator_window(current_project)


def initialize_item_group_creator_window(current_project):
    itemGroupCreatorWindow = ItemGroupCreatorWindow("Create New Item Group", 1200, 800, 0, 0, current_project)
    return itemGroupCreatorWindow


def create_new_item(menuWindow, current_project):
    menuWindow.hide()
    return initialize_item_creator_window(current_project)


def initialize_item_creator_window(current_project):
    itemCreatorWindow = QWidget()
    itemCreatorWindow.setWindowTitle("Create New Item")
    itemGroupChooseWidget = QWidget()

    mainLayout = QHBoxLayout()
    itemCreatorWindow.setLayout(mainLayout)
    checkboxes = {}

    mainWidget = QForm(lambda x: create_new_item_files(x, current_project, checkboxes))
    mainLayout.addWidget(mainWidget)
    mainWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    nameLineEdit = mainWidget.addRow("Item Name:", "name")
    idLineEdit = mainWidget.addRow("Custom ID:", "id")
    imagePickerWidget = mainWidget.addWidgetRow("Item Texture:", QFilePathBox("Choose Texture", "folder.png", lambda x: x, "Images (*.png)", False), "texturePath")
    mainWidget.addSubmitButtonRow("Create Item")

    nameLineEdit.textChanged.connect(lambda: idLineEdit.setText(get_valid_id(nameLineEdit)))
    imagePickerWidget.getLineEdit().textChanged.connect(lambda: imagePickerWidget.setIcon(imagePickerWidget.text()))

    idValidator = QRegExpValidator(QRegExp("[a-z_]+"))
    mainWidget.addValidator(idValidator, idLineEdit)

    itemGroupChooseLayout = QFormLayout()
    mainLayout.addWidget(itemGroupChooseWidget)
    itemGroupChooseWidget.setLayout(itemGroupChooseLayout)

    itemGroupChooseWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    itemGroups = get_item_groups(current_project)
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
            checkbox = QCheckBox(value)
            checkbox.setStyleSheet("margin-left: 60px;")
            itemGroupChooserLayout.addRow(checkbox)
            checkboxes[key] = checkbox

    return itemCreatorWindow


def get_item_groups(current_project):
    item_groups = {}
    if os.path.isdir(f"{current_project}/item_groups"):
        for file in os.listdir(f"{current_project}/item_groups"):
            with open(os.path.join(current_project, "item_groups", file)) as f:
                item_groups[file] = json.loads(f.read())["name"]
    return item_groups



def create_new_item_files(form, current_project, checkboxes):
    values = form.getValues()
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
    
    for key, checkbox in checkboxes.items():
        if checkbox.checkState() == 2:
            content = None
            with open(os.path.join(current_project, "item_groups", key), "r") as f:
                content = json.loads(f.read())

            with open(os.path.join(current_project, "item_groups", key), "w") as f:
                content["items"].append(os.path.join(current_project, "items", values["id"]+".json"))
                f.write(json.dumps(content))
