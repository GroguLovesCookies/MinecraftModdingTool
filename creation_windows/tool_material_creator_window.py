from creation_windows.creation_window import CreationWindow
import os, json
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from form import QItemBrowseBox


class ToolMaterialCreatorWindow(CreationWindow):
    def initialize_layout(self):
        self.setCentralWidget(self.form)

    def initialize_form(self):
        super().initialize_form()

        miningLevel = self.form.addRow("Mining Level:", "miningLevel")
        miningLevelValidator = QIntValidator(0, 999)
        miningLevel.setValidator(miningLevelValidator)

        durability = self.form.addRow("Durability:", "durability")
        durabilityValidator = QIntValidator(0, 9999)
        durability.setValidator(durabilityValidator)

        miningSpeed = self.form.addRow("Mining Speed:", "miningSpeed")
        miningSpeedValidator = QDoubleValidator(0, 99, 2)
        miningSpeed.setValidator(miningSpeedValidator)

        attackDamage = self.form.addRow("Attack Damage:", "attackDamage")
        attackDamageValidator = QDoubleValidator(0, 99, 1)
        attackDamage.setValidator(attackDamageValidator)

        attackDamage = self.form.addRow("Attack Speed:", "attackSpeed")
        attackDamageValidator = QDoubleValidator(0, 99, 1)
        attackDamage.setValidator(attackDamageValidator)

        enchantability = self.form.addRow("Enchantability:", "enchantability")
        enchantabilityValidator = QIntValidator(0, 99)
        enchantability.setValidator(enchantabilityValidator)

        repairItem = self.form.addWidgetRow("Repair Item:", QItemBrowseBox("Select Repair Item", "icons/folder.png", lambda x: x, self.current_project), "repairItem")
        self.form.addSubmitButtonRow("Create")

    def handle_creation(self, form):
        values = form.getValues()

        if not os.path.isdir(os.path.join(self.current_project, "tool_materials")):
            os.mkdir(os.path.join(self.current_project, "tool_materials"))

        with open(os.path.join(self.current_project, "tool_materials", values["id"] + ".json"), "w") as f:
            values.pop("currentProject")
            f.write(json.dumps(values))
        super().handle_creation(form)
