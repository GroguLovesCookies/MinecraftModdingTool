from creation_windows.creation_window import CreationWindow
from form import QItemBrowseBox
import os
import json
from list_widget import QListWidget
from item_browser import QItemSelectorWindow
from PyQt5.QtWidgets import QPushButton


class ItemGroupCreatorWindow(CreationWindow):
    def __init__(self, title, w, h, x, y, current_project, path=""):

        self.values = {}
        self.listWidget = QListWidget(self.values)
        self.window = None

        super().__init__(title, w, h, x, y, current_project, path)

    def get_form_values(self, path):
        with open(path, "r") as f:
            data = json.loads(f.read())
        self.updateList(data["items"])
        return {"name": data["name"], "iconItem": data["icon"], "id": data["id"]}

    def handle_creation(self, form):
        values = form.getValues()
        name = values["name"]
        group_id = values["id"]
        current_project = values["currentProject"]
        icon = values["iconItem"]
        if not os.path.isdir(f"{current_project}/item_groups"):
            os.mkdir(f"{current_project}/item_groups")
        with open(f"{current_project}/item_groups/{group_id}.json", "w") as f:
            f.write(json.dumps({"name": name, "items": self.listWidget.text(), "icon": icon, "id": values["id"]}))

        super().handle_creation(form)

    def initialize_form(self):
        super().initialize_form()
        itemChosenWidget = self.form.addWidgetRow("Icon Item:", QItemBrowseBox("Select Items", "icons/folder.png", lambda x: x, self.current_project), "iconItem")

        chooseMembersButton = QPushButton("Choose Member Items")
        chooseMembersButton.clicked.connect(self.create_selector_window)
        chooseMembersWidget = self.form.addWidgetRow("Items:", chooseMembersButton, "memberItems")

        self.form.layout.addWidget(self.listWidget)

        submitButton = self.form.addSubmitButtonRow("Create")
        print(self.form.getValues())

    def initialize_layout(self):
        self.setCentralWidget(self.form)

    def create_selector_window(self):
        self.window = QItemSelectorWindow([lambda x: True], "Select Items", 1200, 800, quit_function=self.updateList, current_project=self.current_project)

    def updateList(self, new):
        self.listWidget.update_values({i: val for i, val in enumerate(new)})