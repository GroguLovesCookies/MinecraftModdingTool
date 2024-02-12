from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QLabel, QFileDialog, QRadioButton
from PyQt5.QtGui import QIcon
import sys
import os
import json


SELECTED_TEMPLATE = 0
def create_new_project():
    global menuWindow
    menuWindow.hide()
    print("New Project Created")
    menuWindow = initalize_new_project_window()
    menuWindow.show()


def open_new_project():
    print("Open Project")


def get_project_id(fileTextbox, filepathTextbox, outputLabel):
    first_id = "_".join(fileTextbox.text().lower().split())

    path = filepathTextbox.text()
    if os.path.isdir(path):
        needs_new = first_id in os.listdir(path)
        i = 1
        while needs_new:
            new_id = first_id + "(" + str(i) + ")"
            needs_new = new_id in os.listdir(path)
            if not needs_new:
                first_id = new_id
            i += 1
        outputLabel.setText(first_id)
            

def create_project_files(fileTextbox, filepathTextbox, outputLabel):
    file_id = outputLabel.text()
    file_path = filepathTextbox.text()
    if file_id == "":
        return
    else:
        if os.path.isdir(file_path):
            os.mkdir(f"{file_path}/{file_id}")
            with open(f"{file_path}/{file_id}/properties.json", "w") as f:
                f.write(json.dumps({"title": fileTextbox.text(), "template": SELECTED_TEMPLATE}))


def change_selected_template(target):
    global SELECTED_TEMPLATE
    if SELECTED_TEMPLATE != target:
        SELECTED_TEMPLATE = target 
        print(SELECTED_TEMPLATE)


def open_browse_new_project(outputTextbox):
    global menuWindow
    file = str(QFileDialog.getExistingDirectory(menuWindow, "Select Directory", outputTextbox.text()))
    outputTextbox.setText(file)


def initalize_new_project_window():
    newProjectWindow = QWidget()
    newProjectWindow.resize(1200, 800)
    newProjectWindow.setWindowTitle("New Project")

    mainLayout = QHBoxLayout(newProjectWindow)
    newProjectWindow.setLayout(mainLayout)
    
    templatesWidget = QWidget(newProjectWindow)
    mainLayout.addWidget(templatesWidget)

    templateLayout = QFormLayout(templatesWidget)
    templatesWidget.setLayout(templateLayout)
    templatesWidget.setFixedWidth(500)

    radioButtonTemplateOne = QRadioButton("Template 1")
    templateLayout.addRow(radioButtonTemplateOne)
    radioButtonTemplateOne.toggled.connect(lambda: change_selected_template(1))

    radioButtonTemplateTwo = QRadioButton("Template 2")
    templateLayout.addRow(radioButtonTemplateTwo)
    radioButtonTemplateTwo.toggled.connect(lambda: change_selected_template(2))

    radioButtonTemplateThree = QRadioButton("Template 3")
    templateLayout.addRow(radioButtonTemplateThree)
    radioButtonTemplateThree.toggled.connect(lambda: change_selected_template(3))

    radioButtonNoTemplate = QRadioButton("No Template")
    templateLayout.addRow(radioButtonNoTemplate)
    radioButtonNoTemplate.setChecked(True)
    radioButtonNoTemplate.toggled.connect(lambda: change_selected_template(0))

    detailsWidget = QWidget(newProjectWindow)
    mainLayout.addWidget(detailsWidget)
    detailsWidget.setFixedWidth(680)

    formLayout = QFormLayout()
    
    nameLineEdit = QLineEdit(detailsWidget)
    formLayout.addRow("Project Name:", nameLineEdit)

    savePathLabel = QLabel(detailsWidget)
    formLayout.addRow("Save ID:", savePathLabel)

    filepathContainer = QWidget(detailsWidget)
    filepathLineEdit = QLineEdit(detailsWidget)
    filepathLineEdit.setText(os.getcwd())

    filepathBrowseButton = QPushButton()
    filepathBrowseButton.setIcon(QIcon("folder.png"))
    filepathBrowseButton.clicked.connect(lambda:open_browse_new_project(filepathLineEdit))
    filepathLineEdit.textChanged.connect(lambda: get_project_id(nameLineEdit, filepathLineEdit, savePathLabel))
    nameLineEdit.textChanged.connect(lambda: get_project_id(nameLineEdit, filepathLineEdit, savePathLabel))

    filepathLayout = QHBoxLayout(filepathContainer)
    filepathContainer.setLayout(filepathLayout)

    filepathLayout.addWidget(filepathLineEdit)
    filepathLayout.addWidget(filepathBrowseButton)

    formLayout.addRow("File Path:", filepathContainer)

    createButton = QPushButton("Create Project")
    formLayout.addRow(createButton)
    createButton.clicked.connect(lambda: create_project_files(nameLineEdit, filepathLineEdit, savePathLabel))
    createButton.clicked.connect(lambda: get_project_id(nameLineEdit, filepathLineEdit, savePathLabel))

    detailsWidget.setLayout(formLayout)

    return newProjectWindow


if __name__ == "__main__":
    menu_buttons = []

    app = QApplication(sys.argv)

    menuWindow = QWidget()
    menuWindow.resize(1200, 800)
    menuWindow.setWindowTitle("Minecraft Modding Tool")
    menuWindow.show()

    windowParent = QWidget(menuWindow)
    windowParent.resize(600, 600)
    windowParent.show()

    windowLayout = QVBoxLayout(windowParent)
    windowParent.setLayout(windowLayout)

    windowParent.move(menuWindow.width()//2 - windowParent.width()//2, menuWindow.height()//2 - windowParent.height()//2)

    new_button = QPushButton("+ New Project", menuWindow)
    new_button.clicked.connect(create_new_project)
    windowLayout.addWidget(new_button, 2)
    menu_buttons.append(new_button)

    open_button = QPushButton("Open Project", menuWindow)
    open_button.clicked.connect(open_new_project)
    windowLayout.addWidget(open_button, 2)
    menu_buttons.append(open_button)

    for button in menu_buttons:
        button.setFixedHeight(600//len(menu_buttons) - 10)

    sys.exit(app.exec_())