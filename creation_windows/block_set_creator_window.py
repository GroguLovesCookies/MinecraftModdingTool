from creation_windows.creation_window import CreationWindow
from creation_windows.recipe_creator_window import RecipeCreatorWindow
from form import QFormList, QForm, QCustomComboBox, QCustomCheckBox, QCustomLineEdit, QItemBrowseBox, QFilePathBox, QCraftingGrid
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLabel, QPushButton
import os, shutil, json
from copy import deepcopy


class BlockSetCreatorWindow(CreationWindow):
    requiredFields = {"Slab": [], "Stairs": [], "Button": ["pressTime", "arrowTriggerable"], "Pressure Plate": ["itemTriggerable"],
    "Fence": [], "Fence Gate": [], "Wall": [], "Door": ["handOpenableDoor", "bottomTexture", "topTexture", "itemTexture"], 
    "Trapdoor": ["handOpenableTrapdoor", "trapdoorTexture"]}

    def initialize_form(self):
        super().initialize_form()

        blockPrefix = self.form.addRow("Block Prefix:", "blockPrefix")
        mainBlockModel = self.form.addWidgetRow("Model Block:", QItemBrowseBox("Select Block", "icons/folder.png", lambda x: x, self.current_project), "mainModelBlock")

        blockList = self.form.addWidgetWithField(QFormList(self.generate_form, "Add Block", "Remove Block"), "blocks")
        blockList.setMinimumHeight(400)

        for i in range(9):
            blockList.add_form({"blockType": i, "name": lambda x: blockPrefix.text() + " " + x.getFieldValue("blockType")})

        blockPrefix.textChanged.connect(lambda: blockList.set_values({"name": lambda x: blockPrefix.text() + " " + x.getFieldValue("blockType")}))
        self.form.addSubmitButtonRow("Create")

    def initialize_layout(self):
        self.setCentralWidget(self.form)

    def generate_form(self):
        block_form = QForm(lambda x: x)

        block_type = block_form.addWidgetWithField(QCustomComboBox("Block Type", ["Slab", "Stairs", "Button", "Pressure Plate", "Fence", "Fence Gate", "Wall", "Door", "Trapdoor"]), "blockType")
        block_name = block_form.addRow("Name:", "name")
        block_id = block_form.addRow("ID:", "id")
        block_name.textChanged.connect(lambda: block_id.setText(CreationWindow.get_valid_id(block_name)))
        block_model_label = QLabel("Different Model Block:")
        block_model_input = QItemBrowseBox("Select Model Block", "icons/folder.png", lambda x: x, self.current_project)
        block_form.layout.addRow(block_model_label, block_model_input)
        block_form.fields["blockModel"] = block_model_input

        different_recipe = block_form.addWidgetWithField(QCustomCheckBox("Custom Recipe"), "hasCustomRecipe")
        different_recipe.checkbox.toggled.connect(lambda: self.createRecipeWindow(different_recipe, block_form))
        customRecipe = block_form.addHiddenInput("customRecipe")
        customRecipe.textChanged.connect(lambda: print(customRecipe.text()))



        buttonPressTime = block_form.addWidgetWithField(QCustomLineEdit("Press Time (Ticks):"), "pressTime")
        buttonPressTimeValidator = QIntValidator(0, 999)
        buttonPressTime.lineEdit.setValidator(buttonPressTimeValidator)
        buttonArrow = block_form.addWidgetWithField(QCustomCheckBox("Can Be Triggered By Arrows:"), "arrowTriggerable")

        pressurePlateItemTrigger = block_form.addWidgetWithField(QCustomCheckBox("Can Be Triggered By Items:"), "itemTriggerable")

        trapdoorOpenableByHand = block_form.addWidgetWithField(QCustomCheckBox("Can Be Opened By Hand"), "handOpenableTrapdoor")
        doorOpenableByHand = block_form.addWidgetWithField(QCustomCheckBox("Can Be Opened By Hand"), "handOpenableDoor")

        doorBottomTexture, labelTop = block_form.addWidgetRow("Door Bottom Texture:", 
        QFilePathBox("Choose Texture", "icons/folder.png", lambda x: x, "Images (*.png)", False), "bottomTexture", True)
        doorTopTexture, labelBottom = block_form.addWidgetRow("Door Top Texture:",
        QFilePathBox("Choose Texture", "icons/folder.png", lambda x: x, "Images (*.png)", False), "topTexture", True)
        doorItemTexture, labelItem = block_form.addWidgetRow("Door Item Texture:",
        QFilePathBox("Choose Texture", "icons/folder.png", lambda x: x, "Images (*.png)", False), "itemTexture", True)
        
        trapdoorTexture, labelTrapdoor = block_form.addWidgetRow("Trapdoor Texture:",
        QFilePathBox("Choose Texture", "icons/folder.png", lambda x: x, "Images (*.png)", False), "trapdoorTexture", True)

        block_type.combobox.currentIndexChanged.connect(lambda: self.toggleVisibleElements(block_type, 
        [buttonPressTime, buttonArrow], 
        [pressurePlateItemTrigger], 
        [doorOpenableByHand, doorTopTexture, doorBottomTexture, doorItemTexture, labelBottom, labelTop, labelItem], 
        [trapdoorOpenableByHand, trapdoorTexture, labelTrapdoor], 
        [block_model_input, block_model_label]))

        return block_form

    def createRecipeWindow(self, checkbox, form):
        if checkbox.checkbox.isChecked():
            recipeWindow = RecipeCreatorWindow("Custom Recipe", 1200, 800, 200, 100, self.current_project, True, lambda x: form.setValues({"customRecipe": json.dumps(x)}))
            recipeWindow.show()

    def toggleVisibleElements(self, block_type, button, pressure_plate, door, trapdoor, not_door_trapdoor):
        if block_type.text() == "Button":
            self.setVisibilities(True, *button)
            self.setVisibilities(False, *pressure_plate)
            self.setVisibilities(False, *door)
            self.setVisibilities(False, *trapdoor)
            self.setVisibilities(True, *not_door_trapdoor)
        elif block_type.text() == "Pressure Plate":
            self.setVisibilities(False, *button)
            self.setVisibilities(True, *pressure_plate)
            self.setVisibilities(False, *door)
            self.setVisibilities(False, *trapdoor)
            self.setVisibilities(True, *not_door_trapdoor)
        elif block_type.text() == "Door":
            self.setVisibilities(False, *button)
            self.setVisibilities(False, *pressure_plate)
            self.setVisibilities(True, *door)
            self.setVisibilities(False, *trapdoor)
            self.setVisibilities(False, *not_door_trapdoor)
        elif block_type.text() == "Trapdoor":
            self.setVisibilities(False, *button)
            self.setVisibilities(False, *pressure_plate)
            self.setVisibilities(False, *door)
            self.setVisibilities(True, *trapdoor)
            self.setVisibilities(False, *not_door_trapdoor)
        else:
            self.setVisibilities(False, *button)
            self.setVisibilities(False, *pressure_plate)
            self.setVisibilities(False, *door)
            self.setVisibilities(False, *trapdoor)
            self.setVisibilities(True, *not_door_trapdoor)


    def handle_creation(self, form):
        values = form.getValues()
        if not os.path.exists(os.path.join(self.current_project, "block_sets")):
            os.mkdir(os.path.join(self.current_project, "block_sets"))

        with open(os.path.join(self.current_project, "properties.json"), "r") as f:
            properties = json.loads(f.read())

        with open(os.path.join(self.current_project, "block_sets", values["id"] + ".json"), "w") as f:
            f.write(json.dumps(values))
        
        for block in values["blocks"]:
            block_id = block["blockModel"].split(":")[1] if block["blockModel"] != "" else values["mainModelBlock"].split(":")[1]
            with open(os.path.join(self.current_project, "blocks", block_id + ".json"), "r+") as f:
                contents = json.loads(f.read())
                contents["generatePool"] = True
                f.seek(0)
                f.truncate(0)
                f.write(json.dumps(contents))

            if block["blockType"] == "Door":
                shutil.copy(block["bottomTexture"], os.path.join(self.current_project, "textures", f"{block_id}_door_bottom.png"))
                block["bottomTexture"] = os.path.join(self.current_project, "textures", f"{block_id}_door_bottom.png")
                shutil.copy(block["topTexture"], os.path.join(self.current_project, "textures", f"{block_id}_door_top.png"))
                block["topTexture"] = os.path.join(self.current_project, "textures", f"{block_id}_door_top.png")
                shutil.copy(block["itemTexture"], os.path.join(self.current_project, "textures", f"{block_id}_door.png"))
                block["itemTexture"] = os.path.join(self.current_project, "textures", f"{block_id}_door.png")
            if block["blockType"] == "Trapoor":
                shutil.copy(block["trapdoorTexture"], os.path.join(self.current_project, "textures", f"{block_id}_.png"))
                block["trapdoorTexture"] = os.path.join(self.current_project, "textures", f"{block_id}_trapdoor.png")

            with open(os.path.join(self.current_project, "blocks", block["id"] + ".json"), "w") as f:
                data = {"blockset": values["id"]}
                fields = ["name", "id", "blockModel", "hasCustomRecipe", "blockType"]
                fields.extend(BlockSetCreatorWindow.requiredFields[block["blockType"]])
                for field in fields:
                    data[field] = deepcopy(block[field])

                data["blockModel"] = properties["mod_id"] + ":" + block_id
                data["id"] = properties["mod_id"] + ":" + data["id"]
                f.write(json.dumps(data))

            if block["hasCustomRecipe"]:
                recipe = json.loads(block["customRecipe"])
                recipe["outputItem"] = properties["mod_id"] + ":" + block["id"]
            else:
                recipe = BlockSetCreatorWindow.getRecipeFromBlockType(block["blockType"], block_id, block, self.current_project, properties["mod_id"])

            with open(os.path.join(self.current_project, "recipes", f"{recipe['id']}.json"), "w") as f:
                f.write(json.dumps(recipe))
        super().handle_creation(form)


    @staticmethod
    def getRecipeFromBlockType(blockType, baseBlock, block, currentProject, modID):
        with open(os.path.join(currentProject, "blocks", baseBlock + ".json"), "r") as f:
            baseBlockJSON = json.loads(f.read())

        name = f"{block['name']} from {baseBlockJSON['name']}"
        recipe_id = f"{'_'.join(name.lower().split())}"
        outputItem = modID + ":" + block['id']

        data = {"name": name, "id": recipe_id, "outputItem": outputItem, "key": {'A': modID + ":" + baseBlock}}

        if blockType == "Slab":
            data["outputCount"] = 6
            data["patterns"] = ['AAA']
        elif blockType == "Stairs":
            data["outputCount"] = 4
            data["patterns"] = ['  A', ' AA', 'AAA']
        elif blockType == "Button":
            data["inputs"] = {modID + ":" + baseBlock: 1}
            data["outputCount"] = 1
        elif blockType == "Pressure Plate":
            data["patterns"] = ['AA']
            data["outputCount"] = 1
        elif blockType == "Fence":
            data["patterns"] = ['ABA', 'ABA']
            data["key"]["B"] = "minecraft:stick"
            data["outputCount"] = 3
        elif blockType == "Fence Gate":
            data["patterns"] = ['BAB', 'BAB']
            data["key"]["B"] = "minecraft:stick"
            data["outputCount"] = 1
        elif blockType == "Wall":
            data["patterns"] = ['AAA', 'AAA']
            data["outputCount"] = 6
        elif blockType == "Door":
            data["patterns"] = ['AA', 'AA', 'AA']
            data["outputCount"] = 3
        elif blockType == "Trapdoor":
            data["patterns"] = ['AAA', 'AAA']
            data["outputCount"] = 2

        return data


    def setVisibilities(self, visibility, *args):
        for arg in args:
            arg.setVisible(visibility)
