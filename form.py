from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFormLayout, QFileDialog
from PyQt5.QtGui import QIcon, QRegExpValidator, QValidator


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

    def addLabelRow(self, labelLabel, labelText, fieldID):
        label = QLabel(labelText)
        self.layout.addRow(labelLabel, label)
        self.fields[fieldID] = label
        return label

    def addSubmitButtonRow(self, label):
        button = QPushButton(label)
        button.clicked.connect(self.submit)
        self.layout.addRow(button)

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


class QFilePathBox(QWidget):
    def __init__(self, fileDialogTitle, folderIcon, filepathCallback, *args, **kwargs):
        super(QFilePathBox, self).__init__(*args, **kwargs)

        self.fileDialogTitle = fileDialogTitle
        self.folderIcon = folderIcon
        self.filepathCallback = filepathCallback

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.filepathLineEdit = QLineEdit()
        self.layout.addWidget(self.filepathLineEdit)

        self.browseButton = QPushButton()
        self.browseButton.setIcon(QIcon(self.folderIcon))
        self.browseButton.clicked.connect(self.onBrowse)
        self.layout.addWidget(self.browseButton)


    def setText(self, text):
        self.filepathLineEdit.setText(text)

    def text(self):
        return self.filepathLineEdit.text()

    def onBrowse(self):
        file = str(QFileDialog.getExistingDirectory(self, self.fileDialogTitle, self.text()))
        self.filepathLineEdit.setText(file)

    def getLineEdit(self):
        return self.filepathLineEdit
    
    def getBrowseButton(self):
        return self.browseButton