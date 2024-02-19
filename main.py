from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, 
QLineEdit, QLabel, QFileDialog, QRadioButton, QGridLayout, QSizePolicy, QScrollArea,
QTabWidget)
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp
import sys
import os
import json
from id_generator import generate_random_id, validate_id
from handle_creations import *
from form import QForm, QFilePathBox
from item_browser import QVanillaItemIcon, QItemSelectorWindow
import item_filters
from creation_windows.creation_window import CreationWindow
from creation_windows.item_group_creator_window import ItemGroupCreatorWindow
from list_widget import QListWidget


CURRENT_PROJECT = ""
with open("settings.json", "r") as f:
    previous_settings = json.loads(f.read())
    CURRENT_PROJECT = previous_settings["previous_project"]

SELECTED_TEMPLATE = 0
SELECTED_ITEMS = []

def get_chosen_items(items):
    global SELECTED_ITEMS
    SELECTED_ITEMS = items
    print(SELECTED_ITEMS)

def set_current_project(target):
    global CURRENT_PROJECT
    CURRENT_PROJECT = target
    with open("settings.json", "r") as f:
        previous_settings = json.loads(f.read())
        previous_settings["previous_project"] = target
    with open("settings.json", "w") as f:
        f.write(json.dumps(previous_settings))


def create_new_project():
    global menuWindow
    menuWindow.hide()
    print("New Project Created")
    menuWindow = initalize_project_creation_window()
    showWindow(menuWindow)


def open_new_project():
    global menuWindow
    menuWindow.hide()
    print("Opening Created Project")
    menuWindow = initalize_project_editing_window()
    showWindow(menuWindow, True)


def open_project():
    global menuWindow, CURRENT_PROJECT
    print("Open Existing Project")
    chosenPath = str(QFileDialog.getExistingDirectory(menuWindow, "Select Project", os.getcwd()))

    if "properties.json" not in os.listdir(chosenPath):
        return
    with open(f"{chosenPath}/properties.json") as f:
        properties = json.loads(f.read())
        print(properties)
        if "verification_id" not in properties.keys():
            return
        if not validate_id(properties["verification_id"]):
            return
    set_current_project(chosenPath)
    
    menuWindow.hide()
    menuWindow = initalize_project_editing_window()
    showWindow(menuWindow, True)
    


def get_project_id(form):
    values = form.getValues()

    first_id = "_".join(values["name"].lower().split())
    path = values["saveDirectory"]
    if os.path.isdir(path):
        needs_new = first_id in os.listdir(path)
        i = 1
        while needs_new:
            new_id = first_id + "(" + str(i) + ")"
            needs_new = new_id in os.listdir(path)
            if not needs_new:
                first_id = new_id
            i += 1
        form.setValues({"saveID": first_id})
            

def create_project_files(form):
    global SELECTED_TEMPLATE, CURRENT_PROJECT

    values = form.getValues()
    file_id = values["saveID"]
    file_path = values["saveDirectory"]
    if file_id == "":
        return
    else:
        if os.path.isdir(file_path):
            os.mkdir(f"{file_path}/{file_id}")
            with open(f"{file_path}/{file_id}/properties.json", "w") as f:
                f.write(json.dumps({
                    "title": values["name"], 
                    "template": SELECTED_TEMPLATE, 
                    "verification_id": generate_random_id(),
                    "mod_id": values["modID"]
                }))
        set_current_project(f"{file_path}/{file_id}")
        open_new_project()


def change_selected_template(target):
    global SELECTED_TEMPLATE
    if SELECTED_TEMPLATE != target:
        SELECTED_TEMPLATE = target 
        print(SELECTED_TEMPLATE)


def open_browse_new_project(outputTextbox):
    global menuWindow
    file = str(QFileDialog.getExistingDirectory(menuWindow, "Select Directory", outputTextbox.text()))
    outputTextbox.setText(file)


def initalize_project_creation_window():
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

    detailsWidget = QForm(create_project_files, newProjectWindow)
    mainLayout.addWidget(detailsWidget)
    detailsWidget.setFixedWidth(680)

    nameLineEdit = detailsWidget.addRow("Project Name:", "name")
    savePathLabel = detailsWidget.addLabelRow("Save ID:", "-", "saveID")
    filepathBox = detailsWidget.addWidgetRow("Save At:", QFilePathBox("Select Directory", "icons/folder.png", lambda x: x), "saveDirectory")
    modIdLineEdit = detailsWidget.addRow("Mod ID:", "modID")
    detailsWidget.addSubmitButtonRow("Create Project")

    modIdValidator = QRegExpValidator(QRegExp("[a-z_]+"))
    detailsWidget.addValidator(modIdValidator, modIdLineEdit)
    

    filepathLineEdit = filepathBox.getLineEdit()
    filepathLineEdit.textChanged.connect(lambda: get_project_id(detailsWidget))
    nameLineEdit.textChanged.connect(lambda: get_project_id(detailsWidget))

    detailsWidget.setValues({"saveDirectory": os.getcwd()})

    return newProjectWindow


def showWindow(inputWindow, maximized=False):
    global menuWindow
    menuWindow = inputWindow
    menuWindow.setObjectName("mainWindow")
    if not maximized:
        menuWindow.show()
    else:
        menuWindow.showMaximized()


def initalize_project_editing_window():
    global menuWindow
    editProjectWindow = QWidget()

    buttonValues = [
        ("New Creative\nMode Tab", lambda: showWindow(create_new_item_group(menuWindow, CURRENT_PROJECT)), (0, 0, 1, 1)),
        ("New Item", lambda: showWindow(create_new_item(menuWindow, CURRENT_PROJECT)), (0, 1, 1, 1)),
        ("New Block", lambda: showWindow(create_new_block(menuWindow, CURRENT_PROJECT)), (0, 2, 1, 1)),
        ("New Recipe", lambda: showWindow(create_new_recipe(menuWindow, CURRENT_PROJECT)), (1, 0, 1, 1)),
        ("New Armor\nSet", lambda: True, (1, 1, 1, 1)),
        ("New Block\nSet", lambda: True, (1, 2, 1, 1)),
        ("New Tool\nSet", lambda: True, (2, 0, 1, 1)),
        ("New Armor\nSet", lambda: True, (2, 1, 1, 1)),
        ("New Block\nSet", lambda: True, (2, 2, 1, 1)),
        ("New Tool\nSet", lambda: True, (3, 0, 1, 1)),
        ("New Armor\nSet", lambda: True, (3, 1, 1, 1)),
        ("New Block\nSet", lambda: True, (3, 2, 1, 1)),
        ("New Tool\nSet", lambda: True, (4, 0, 1, 1)),
        ("New Armor\nSet", lambda: True, (4, 1, 1, 1)),
        ("New Block\nSet", lambda: True, (4, 2, 1, 1)),
        ("New Tool\nSet", lambda: True, (5, 0, 1, 1)),
        ("New Armor\nSet", lambda: True, (5, 1, 1, 1)),
        ("New Block\nSet", lambda: True, (5, 2, 1, 1))
    ]

    projectProperties = {}
    if os.path.isdir(CURRENT_PROJECT):
        with open(f"{CURRENT_PROJECT}/properties.json", "r") as f:
            projectProperties = json.loads(f.read())
    print(projectProperties)

    editProjectWindow.setWindowTitle(projectProperties["title"])
    
    createLayout = QHBoxLayout()
    editProjectWindow.setLayout(createLayout)

    scrollArea = QScrollArea()
    createLayout.addWidget(scrollArea, 42)
    scrollArea.setWidgetResizable(True)

    scrollContent = QWidget()
    scrollContent.setObjectName("scroll")
    scrollLayout = QGridLayout()
    scrollContent.setLayout(scrollLayout)
    scrollArea.setWidget(scrollContent)

    buttonWidth = 250

    for button_name, button_callback, button_coords in buttonValues:
        button = QPushButton(button_name)
        button.clicked.connect(button_callback)
        scrollLayout.addWidget(button, *button_coords, Qt.AlignmentFlag.AlignTop)
        button.setObjectName("hoverableButton")
        button.setFixedSize(buttonWidth, buttonWidth)

    
    scrollArea.setObjectName("scrollArea")

    editArea = QWidget()
    editLayout = QVBoxLayout()
    editArea.setLayout(editLayout)
    createLayout.addWidget(editArea, 58)

    editLabel = QLabel("Edit")
    editLabel.setObjectName("itemGroupChoiceHeading")
    editLayout.addWidget(editLabel)

    editTabs = QTabWidget()
    editLayout.addWidget(editTabs)

    values = {}
    if os.path.isdir(os.path.join(CURRENT_PROJECT, "item_groups")):
        for group in os.listdir(os.path.join(CURRENT_PROJECT, "item_groups")):
            with open(os.path.join(CURRENT_PROJECT, "item_groups", group), "r") as f:
                values[os.path.join(CURRENT_PROJECT, "item_groups", group)] = json.loads(f.read())["name"]
    editItemGroupsWidget = QListWidget(values, handle_item_group_click)

    editItemsWidget = QWidget()

    editTabs.addTab(editItemGroupsWidget, "Item Groups")
    editTabs.addTab(editItemsWidget, "Items")
    

    
    return editProjectWindow

def handle_item_group_click(x):
    global menuWindow
    showWindow(create_new_item_group(menuWindow, CURRENT_PROJECT, x))

if __name__ == "__main__":
    CreationWindow.onDestroy = lambda: showWindow(initalize_project_editing_window(), True)
    menu_buttons = []

    app = QApplication(sys.argv)
    

    menuWindow = QWidget()
    menuWindow.setAutoFillBackground(True)
    menuWindow.resize(1200, 800)
    menuWindow.setWindowTitle("Minecraft Modding Tool")
    showWindow(menuWindow)
    app.setStyleSheet("QWidget { font-family: serif; color: #b8b8b8; font-size: 25px; } \
                        QPushButton { padding: 10px; border: 4px double black; } \
                        #hoverableButton:hover, #falseButton:hover { background-color: #333; } \
                        #mainWindow, QMainWindow { background-color: #222; } \
                        #scroll { background-color: #202020; } \
                        QLineEdit { background-color: transparent; border: none; border-bottom: 2px solid black; padding: 5px; } \
                        QLineEdit:focus { border-bottom: 2px solid #32a89d; } \
                        QLineEdit:hover { background-color: #333; } \
                        #itemGroupChoiceHeading { font-size: 40px; margin-bottom: 5px; }  \
                        QCheckBox::indicator { width: 20px; height: 20px; background-color: transparent; border: 2px solid black; margin-top: 4px; } \
                        QCheckBox::indicator:checked { background-color: #32a89d; } \
                        #scrollArea { border: none; } \
                        QScrollBar { width: 8px; background: transparent; } \
                        QScrollBar::handle { background-color: #32a89d; border-radius: 4px; } \
                        QScrollBar::add-line { border: none; background: none; } \
                        QScrollBar::sub-line { border: none; background: none; } \
                        QRadioButton::indicator { background: none; width: 20px; height: 20px; border: 2px solid black; border-radius: 12px; } \
                        QRadioButton::indicator:checked { background-color: #32a89d; } \
                        QTabWidget { background-color: #202020; border: none; } \
                        QTabBar::tab:!selected { background-color: #202020; } \
                        QTabBar::tab:selected { background-color: #333; } \
                        #falseButton { border: none; } \
                        QComboBox { background-color: #333; border: none; } \
                        QComboBox { padding: 0 10px 0 10px; } \
                        QComboBox:on QListView { padding: -20px; background-color: #333; } \
                        QComboBox::item:selected { background-color: #444; } \
                        QComboBox::drop-down { border: none; }")
    
    if CURRENT_PROJECT == "":
        windowParent = QWidget(menuWindow)
        windowParent.resize(600, 600)
        windowParent.show()

        windowLayout = QVBoxLayout(windowParent)
        windowParent.setLayout(windowLayout)

        windowParent.move(menuWindow.width()//2 - windowParent.width()//2, menuWindow.height()//2 - windowParent.height()//2)

        new_button = QPushButton("+ New Project", menuWindow)
        new_button.clicked.connect(create_new_project)
        new_button.setObjectName("hoverableButton")
        windowLayout.addWidget(new_button, 2)
        menu_buttons.append(new_button)

        open_button = QPushButton("Open Project", menuWindow)
        open_button.clicked.connect(open_project)
        open_button.setObjectName("hoverableButton")
        windowLayout.addWidget(open_button, 2)
        menu_buttons.append(open_button)

        # icon = QVanillaItemIcon("leather_helmet", (32, 32))
        # icon.set_block("redstone_comparator")
        # windowLayout.addWidget(icon)

        for button in menu_buttons:
            button.setFixedHeight(600//len(menu_buttons) - 10)
            button.raise_()
    else:
        menuWindow.hide()
        menuWindow = initalize_project_editing_window()
        showWindow(menuWindow, True)

    sys.exit(app.exec_())