from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFormLayout, QFileDialog, QCheckBox, QComboBox, QGridLayout, QSizePolicy
from PyQt5.QtGui import QIcon, QRegExpValidator, QValidator, QPixmap, QIntValidator
from PyQt5.QtCore import Qt
import os
from item_browser import QItemSelectorWindow, QVanillaItemIcon
import json


def get_vanilla_items():
    with open("resources/item_orders/wiki_order.json", "r") as f:
        return json.loads(f.read())["order"]


class QForm(QWidget):
    def __init__(self, submitCallback, *args, **kwargs):
        super(QForm, self).__init__(*args, **kwargs)

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.fields = {}
        self.validators = {}

        self.submitCallback = submitCallback
    
    def addValidator(self, validator, widget):
        self.validators[widget] = validator

    def addRow(self, labelText, fieldID):
        lineEdit = QLineEdit()
        self.layout.addRow(labelText, lineEdit)
        self.fields[fieldID] = lineEdit
        return lineEdit

    def addWidgetRow(self, labelText, widget, fieldID):
        self.layout.addRow(labelText, widget)
        self.fields[fieldID] = widget
        return widget

    def addWidgetWithoutField(self, widget):
        self.layout.addRow(widget)
        return widget

    def addWidgetWithField(self, widget, fieldID):
        self.layout.addRow(widget)
        self.fields[fieldID] = widget
        return widget

    def addLabelRow(self, labelLabel, labelText, fieldID):
        label = QLabel(labelText)
        self.layout.addRow(labelLabel, label)
        self.fields[fieldID] = label
        return label

    def addSubmitButtonRow(self, label):
        button = QPushButton(label)
        button.clicked.connect(self.submit)
        button.setObjectName("hoverableButton")
        self.layout.addRow(button)
        return button
    
    def addHiddenInput(self, fieldID):
        lineEdit = QLineEdit()
        self.fields[fieldID] = lineEdit

    def setValues(self, values):
        for key, value in values.items():
            self.fields[key].setText(value)

    def getValues(self):
        return {key: value.text() for key, value in self.fields.items()}

    def setFieldValue(self, fieldID, value):
        self.fields[fieldID].setText(value)

    def getFieldValue(self, fieldID):
        return self.fields[fieldID].text()

    def getField(self, fieldID):
        return self.fields[fieldID]

    def submit(self):
        all_valid = True
        for widget, validator in self.validators.items():
            all_valid = validator.validate(widget.text(), 0)[0] == QValidator.State.Acceptable and all_valid
        if all_valid:
            self.submitCallback(self)

    def text(self):
        return self.getValues()


class QFilePathBox(QWidget):
    def __init__(self, fileDialogTitle, folderIcon, filepathCallback, filter="", directory=True, *args, **kwargs):
        super(QFilePathBox, self).__init__(*args, **kwargs)

        self.fileDialogTitle = fileDialogTitle
        self.folderIcon = folderIcon
        self.filepathCallback = filepathCallback
        self.filter = filter
        self.directory = directory

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.filepathLineEdit = QLineEdit()
        self.layout.addWidget(self.filepathLineEdit)

        self.browseButton = QPushButton()
        self.browseButton.setObjectName("hoverableButton")
        self.browseButton.setIcon(QIcon(self.folderIcon))
        self.browseButton.clicked.connect(self.onBrowse)
        self.layout.addWidget(self.browseButton)


    def setText(self, text):
        self.filepathLineEdit.setText(text)

    def text(self):
        return self.filepathLineEdit.text()

    def onBrowse(self):
        if self.directory:
            file = str(QFileDialog.getExistingDirectory(self, self.fileDialogTitle, self.text()))
        else:
            file = str(QFileDialog.getOpenFileName(self, self.fileDialogTitle, self.text(), self.filter)[0])
        self.filepathLineEdit.setText(file)

    def getLineEdit(self):
        return self.filepathLineEdit
    
    def getBrowseButton(self):
        return self.browseButton

    def setIcon(self, path):
        if os.path.isfile(path):
            self.browseButton.setIcon(QIcon(path))


class QItemBrowseBox(QFilePathBox):
    def __init__(self, dialogTitle, dialogIcon, callback, current_project, limit=1, *args, **kwargs):
        super().__init__(dialogTitle, dialogIcon, callback)
        self.current_project = current_project
        self.selected = ""
        self.limit = limit

    def onBrowse(self):
        window = QItemSelectorWindow([lambda x: True], self.fileDialogTitle, 1200, 800, "wiki_order.json", self.limit, self.getSelectedItem, self.current_project)

    def getSelectedItem(self, x):
        self.selected = x[0]
        if ":" not in self.selected:
            self.selected = "minecraft:" + self.selected
        self.setText(self.selected)


class QCustomCheckBox(QWidget):
    def __init__(self, text, *args, **kwargs):
        super(QCustomCheckBox, self).__init__(*args, **kwargs)
        self.checkbox = QCheckBox()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel(text), 90)
        self.layout.addWidget(self.checkbox, 10)

    def text(self):
        return self.checkbox.isChecked()


class QCustomComboBox(QWidget):
    def __init__(self, text, items, *args, **kwargs):
        super(QCustomComboBox, self).__init__(*args, **kwargs)
        self.combobox = QComboBox()
        self.combobox.addItems(items)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel(text), Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.combobox, Qt.AlignmentFlag.AlignLeft)

    def text(self):
        return self.combobox.currentText()


class QCustomLineEdit(QWidget):
    def __init__(self, text, *args, **kwargs):
        super(QCustomLineEdit, self).__init__(*args, **kwargs)
        self.lineEdit = QLineEdit()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel(text), Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.lineEdit, Qt.AlignmentFlag.AlignLeft)

    def text(self):
        return self.lineEdit.text()

    def setText(self, text):
        self.lineEdit.setText(text)


class QHotBar(QWidget):
    vanilla_items = get_vanilla_items()

    def __init__(self, current_project, crafting_grid, *args, **kwargs):
        super(QHotBar, self).__init__(*args, **kwargs)
        self.items = []
        self.current_project = current_project
        self.crafting_grid = crafting_grid

        self.labels = []
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.currentItem = "minecraft:zombie_head"

        for _ in range(9):
            label = QVanillaItemIcon("air", (32, 32), True, lambda x: self.onClick(x))
            label.setStyleSheet("background-color: #333; padding: 10px;")
            self.labels.append(label)
            self.layout.addWidget(label)

        setupPushButton = QPushButton("Change Hotbar")
        setupPushButton.clicked.connect(self.startSetupWindow)
        self.layout.addWidget(setupPushButton)

    def startSetupWindow(self):
        selectorWindow = QItemSelectorWindow([lambda x: True], "Select Items", 1200, 800, limit=9, quit_function=self.setText, current_project=self.current_project)
    
    def setItem(self, widget):
        if self.currentItem.startswith("minecraft:"):
            if self.currentItem.split(":")[1] in self.vanilla_items:
                widget.set_item(self.currentItem.split(":")[1])
            else:
                widget.set_block(self.currentItem.split(":")[1])
        else:
            widget.item_id = self.currentItem
            if self.currentItem in self.modItems:
                with open(os.path.join(self.current_project, "items", self.currentItem.split(":")[1] + ".json"), "r") as f:
                    item = json.loads(f.read())
                    name = item["name"]
                    texture_file = item["texture"]
                    item_id = item["id"]
                    pixmap = QPixmap(texture_file)
                    widget.set_pixmap(pixmap)
            else:
                with open(os.path.join(self.current_project, "blocks", self.currentItem.split(":")[1] + ".json"), "r") as f:
                    item = json.loads(f.read())
                    name = item["name"]
                    texture_file = item["texture"]
                    item_id = item["id"]
                    pixmap = QPixmap(texture_file)
                    widget.set_pixmap(pixmap)
    
    def onClick(self, widget):
        item_id = widget.item_id
        if ":" not in item_id:
            item_id = "minecraft:" + item_id
        self.crafting_grid.currentItem = item_id

    def text(self):
        items = []
        for label in self.labels:
            if ":" not in label.item_id:
                items.append("minecraft:" + label.item_id)
            else:
                items.append(label.item_id)
        return items

    def setText(self, items):
        for item, label in zip(items, self.labels):
            self.currentItem = item
            self.setItem(label)

    @property
    def modItems(self):
        items = []
        for path in os.listdir(os.path.join(self.current_project, "items")):
            with open(os.path.join(self.current_project, "items", path), "r") as f:
                items.append(json.loads(f.read())["id"])

        return items

class QCraftingGrid(QWidget):
    vanilla_items = get_vanilla_items()

    def __init__(self, current_project, *args, **kwargs):
        super(QCraftingGrid, self).__init__(*args, **kwargs)
        self.items = []
        self.current_project = current_project

        self.labels = []
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.resultCount = 0

        self.currentItem = "minecraft:air"

        for i in range(9):
            label = QVanillaItemIcon("air", (32, 32), True, lambda x: self.setItem(x))
            label.setStyleSheet("background-color: #333; padding: 10px;")
            self.labels.append(label)
            self.layout.addWidget(label, i//3, i%3, 1, 1)

        emptyWidget = QWidget()
        emptyWidget.setFixedSize(32*4, 32)
        self.layout.addWidget(emptyWidget, 1, 3, 1, 4)
        
        label = QVanillaItemIcon("air", (32, 32), True, lambda x: self.setItem(x))
        label.setStyleSheet("background-color: #333; padding: 10px;")
        self.layout.addWidget(label, 1, 7, 1, 1)
        self.labels.append(label)

        self.countLineEdit = QLineEdit()
        self.countLineEdit.setValidator(QIntValidator(1, 64))
        self.layout.addWidget(self.countLineEdit, 1, 8, 1, 2)

        
    
    def setItem(self, widget):
        if self.currentItem.startswith("minecraft:"):
            if self.currentItem.split(":")[1] in self.vanilla_items:
                widget.set_item(self.currentItem.split(":")[1])
            else:
                widget.set_block(self.currentItem.split(":")[1])
        else:
            widget.item_id = self.currentItem
            if self.currentItem in self.modItems:
                with open(os.path.join(self.current_project, "items", self.currentItem.split(":")[1] + ".json"), "r") as f:
                    item = json.loads(f.read())
                    name = item["name"]
                    texture_file = item["texture"]
                    item_id = item["id"]
                    pixmap = QPixmap(texture_file)
                    widget.set_pixmap(pixmap)
            else:
                with open(os.path.join(self.current_project, "blocks", self.currentItem.split(":")[1] + ".json"), "r") as f:
                    item = json.loads(f.read())
                    name = item["name"]
                    texture_file = item["texture"]
                    item_id = item["id"]
                    pixmap = QPixmap(texture_file)
                    widget.set_pixmap(pixmap)
    def text(self):
        items = []
        for label in self.labels:
            if ":" not in label.item_id:
                items.append("minecraft:" + label.item_id)
            else:
                items.append(label.item_id)
        items.append(min(64, int(self.countLineEdit.text())))
        return items

    @property
    def modItems(self):
        items = []
        for path in os.listdir(os.path.join(self.current_project, "items")):
            with open(os.path.join(self.current_project, "items", path), "r") as f:
                items.append(json.loads(f.read())["id"])

        return items