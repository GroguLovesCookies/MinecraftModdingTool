import os
import json
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QLabel, QLineEdit, QWidget
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator, QPixmap
from form import QForm, QFilePathBox
import shutil


def create_new_item_group(menuWindow, current_project):
    menuWindow.hide()
    return initialize_item_group_creator_window(current_project)


def get_valid_id(inputLineEdit):
    text = inputLineEdit.text()
    return "_".join(text.lower().split())


def create_new_item_group_file(idLineEdit, nameLineEdit, current_project):
    name = nameLineEdit.text()
    group_id = idLineEdit.text()
    if not os.path.isdir(f"{current_project}/item_groups"):
        os.mkdir(f"{current_project}/item_groups")
    with open(f"{current_project}/item_groups/{group_id}.json", "w") as f:
        f.write(json.dumps({group_id: {"name": name, "items": [], "icon": None}}))



def initialize_item_group_creator_window(current_project):
    itemGroupCreatorWindow = QWidget()
    itemGroupCreatorWindow.resize(1200, 800)
    itemGroupCreatorWindow.setWindowTitle("Create New Item Group")
    
    mainLayout = QHBoxLayout()
    itemGroupCreatorWindow.setLayout(mainLayout)

    formWidget = QWidget()
    formLayout = QFormLayout()
    formWidget.setLayout(formLayout)
    mainLayout.addWidget(formWidget)

    nameLineEdit = QLineEdit()
    formLayout.addRow("Name:", nameLineEdit)

    idLineEdit = QLineEdit()
    formLayout.addRow("Custom ID:", idLineEdit)
    nameLineEdit.textChanged.connect(lambda: idLineEdit.setText(get_valid_id(nameLineEdit)))

    submitButton = QPushButton("Create")
    formLayout.addRow(submitButton)
    submitButton.clicked.connect(lambda:create_new_item_group_file(idLineEdit, nameLineEdit, current_project))

    return itemGroupCreatorWindow


def create_new_item(menuWindow, current_project):
    menuWindow.hide()
    return initialize_item_creator_window(current_project)


def initialize_item_creator_window(current_project):
    itemCreatorWindow = QWidget()
    itemCreatorWindow.setWindowTitle("Create New Item")

    mainLayout = QHBoxLayout()
    itemCreatorWindow.setLayout(mainLayout)

    mainWidget = QForm(lambda x: create_new_item_files(x, current_project), itemCreatorWindow)
    mainLayout.addWidget(mainWidget)

    nameLineEdit = mainWidget.addRow("Item Name:", "name")
    idLineEdit = mainWidget.addRow("Custom ID:", "id")
    imagePickerWidget = mainWidget.addWidgetRow("Item Texture:", QFilePathBox("Choose Texture", "folder.png", lambda x: x, "Images (*.png)", False), "texturePath")
    mainWidget.addSubmitButtonRow("Create Item")

    nameLineEdit.textChanged.connect(lambda: idLineEdit.setText(get_valid_id(nameLineEdit)))
    imagePickerWidget.getLineEdit().textChanged.connect(lambda: imagePickerWidget.setIcon(imagePickerWidget.text()))

    idValidator = QRegExpValidator(QRegExp("[a-z_]+"))
    mainWidget.addValidator(idValidator, idLineEdit)

    itemGroupChooseWidget = QWidget()
    mainLayout.addWidget(itemGroupChooseWidget)

    return itemCreatorWindow


def create_new_item_files(form, current_project):
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
