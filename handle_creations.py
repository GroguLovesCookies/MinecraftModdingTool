import os
import json
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QLabel, QLineEdit, QWidget


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