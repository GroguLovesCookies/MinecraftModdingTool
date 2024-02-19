from creation_windows.creation_window import CreationWindow
from form import QCraftingGrid, QHotBar, QCustomCheckBox
import os
import json


class RecipeCreatorWindow(CreationWindow):
    def handle_creation(self, form):
        values = form.getValues()
        patterns, key = RecipeCreatorWindow.get_pattern_from_list(values["craftingGrid"])

        if not os.path.isdir(os.path.join(values["currentProject"], "recipes")):
            os.mkdir(os.path.join(values["currentProject"], "recipes"))

        with open(os.path.join(values["currentProject"], "recipes", values["id"] + ".json"), "w") as f:
            data = {"name": values["name"], "id": values["id"], "patterns": patterns, "key": key, "outputItem": values["craftingGrid"][-2],
            "outputCount": values["craftingGrid"][-1], "shapeless": values["shapeless"]}
            f.write(json.dumps(data))

        super().handle_creation(form)

    def initialize_form(self):
        super().initialize_form()

        nameLineEdit = self.form.addRow("Name:", "name")
        idLineEdit = self.form.addRow("Custom ID:", "id")
        nameLineEdit.textChanged.connect(lambda: idLineEdit.setText(CreationWindow.get_valid_id(nameLineEdit)))

        craftingGrid = self.form.addWidgetWithField(QCraftingGrid(self.current_project), "craftingGrid")
        self.form.addWidgetWithoutField(QHotBar(self.current_project, craftingGrid))

        self.form.addWidgetWithField(QCustomCheckBox("Shapeless"), "shapeless")

        self.form.addSubmitButtonRow("Create")

    def initialize_layout(self):
        self.setCentralWidget(self.form)

    @staticmethod
    def get_pattern_from_list(grid):
        pattern = ""
        available_symbols = "ABCDEFGHI"
        key = {}
        for item in grid[:9]:
            if item == "minecraft:air":
                pattern += " "
            else:
                if item not in key.keys():
                    key[item] = available_symbols[len(key)]
                pattern += key[item]

        # Prune pattern
        patterns = [pattern[0:3], pattern[3:6], pattern[6:9]]
        while "   " in patterns:
            patterns.remove("   ")

        removeable_column_indices = [i for i in range(3) if False not in [pattern[i] == " " for pattern in patterns]]
        removed = 0
        for column in removeable_column_indices:
            for i in range(len(patterns)):
                list_pattern = list(patterns[i])
                list_pattern.remove(list_pattern[column-removed])
                patterns[i] = "".join(list_pattern)
            removed += 1

        return patterns, {value: letter for letter, value in key.items()}
            