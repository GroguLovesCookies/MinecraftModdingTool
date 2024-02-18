from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFormLayout, QFileDialog, QCheckBox, QComboBox
from PyQt5.QtGui import QIcon, QRegExpValidator, QValidator
from PyQt5.QtCore import Qt
import os
from item_browser import QItemSelectorWindow


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

