from creation_windows.creation_window import CreationWindow
from form import QItemBrowseBox
import os
import json


class ItemGroupCreatorWindow(CreationWindow):
    def handle_creation(self, form):
        values = form.getValues()
        name = values["name"]
        group_id = values["id"]
        current_project = values["currentProject"]
        icon = values["iconItem"]
        if not os.path.isdir(f"{current_project}/item_groups"):
            os.mkdir(f"{current_project}/item_groups")
        with open(f"{current_project}/item_groups/{group_id}.json", "w") as f:
            f.write(json.dumps({"name": name, "items": [], "icon": icon}))

        super().handle_creation(form)

    def initialize_form(self):
        super().initialize_form()

        nameLineEdit = self.form.addRow("Name:", "name")
        idLineEdit = self.form.addRow("Custom ID:", "id")
        itemChosenWidget = self.form.addWidgetRow("Icon Item:", QItemBrowseBox("Select Items", "icons/folder.png", lambda x: x, self.current_project), "iconItem")

        nameLineEdit.textChanged.connect(lambda: idLineEdit.setText(CreationWindow.get_valid_id(nameLineEdit)))

        submitButton = self.form.addSubmitButtonRow("Create")
        print(self.form.getValues())

    def initialize_layout(self):
        self.setCentralWidget(self.form)