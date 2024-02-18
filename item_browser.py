from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFormLayout, QScrollArea, QMainWindow, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QCheckBox, QRadioButton, QButtonGroup
from PyQt5.QtGui import QImage, QPixmap, QColor, QIcon
import json
import item_filters
import os
import numpy


def get_sprite_key():
    with open("resources/spritekey.json") as f:
        return json.loads(f.read())

def get_block_sprite_key():
    with open("resources/spritekey_blocks.json") as f:
        return json.loads(f.read())

def get_spritesheet():
    with open("resources/spritesheet.json") as f:
        return json.loads(f.read())["img"]

def get_block_spritesheet():
    with open("resources/spritesheet_blocks.json") as f:
        return json.loads(f.read())["img"]

def get_loose_blocks():
    data = {}
    for path in os.listdir("resources/loose"):
        if path.endswith(".json"):
            with open(os.path.join("resources/loose", path), "r") as f:
                data[path[:-5]] = json.loads(f.read())["img"]
    return data


class QVanillaItemIcon(QWidget):
    spritesheet = get_spritesheet()
    sprite_key  = get_sprite_key()
    spritesheet_blocks = get_block_spritesheet()
    sprite_key_blocks = get_block_sprite_key()

    def __init__(self, item_id, size, auto_init=True, *args, **kwargs):
        super(QVanillaItemIcon, self).__init__(*args, **kwargs)

        self.item_id = item_id

        self.label = QLabel("")
        self.pixmap = QPixmap(16, 16)
        self.label.setPixmap(self.pixmap)
        self.size = size

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.label)
        self.setLayout(self.mainLayout)

        if auto_init:
            self.set_item(self.item_id)


    def set_item(self, item_id):
        if item_id not in QVanillaItemIcon.sprite_key.keys():
            return
        self.item_id = item_id
        offset_x, offset_y = QVanillaItemIcon.sprite_key[self.item_id]

        image = self.pixmap.toImage()
        image = image.convertToFormat(QImage.Format.Format_ARGB32)
        for x in range(16):
            for y in range(16):
                color = QVanillaItemIcon.spritesheet[y + offset_y*16][x + offset_x*16]
                image.setPixelColor(x, y, QColor(*[color[2], color[1], color[0], color[3]]))

        self.pixmap = QPixmap.fromImage(image)
        self.pixmap = self.pixmap.scaled(*self.size)
        self.label.setPixmap(self.pixmap)

    def set_block(self, block_id):
        if block_id not in QVanillaItemIcon.sprite_key_blocks["loose"]:
            offset_x, offset_y = QVanillaItemIcon.sprite_key_blocks[block_id]
            self.pixmap = QPixmap(32, 32)
            image = self.pixmap.toImage()
            image = image.convertToFormat(QImage.Format.Format_ARGB32)
            for x in range(32):
                for y in range(32):
                    color = QVanillaItemIcon.spritesheet_blocks[y + offset_y*32][x + offset_x*32]
                    image.setPixelColor(x, y, QColor(*[color[2], color[1], color[0], color[3]]))

            self.pixmap = QPixmap.fromImage(image)
            self.pixmap = self.pixmap.scaled(*self.size)
            self.label.setPixmap(self.pixmap)
        else:
            self.pixmap = QPixmap("resources/loose/" + block_id + ".png")
            self.pixmap = self.pixmap.scaledToWidth(*self.size)
            self.label.setPixmap(self.pixmap)

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap.scaled(*self.size)
        self.label.setPixmap(self.pixmap)


class QItemSelectorWindow(QMainWindow):
    itemsToDifferentNames = \
    {"writable_book": "book_and_quill", "map": "empty_map", "filled_map": "map", "cooked_beef": "steak", "dragon_breath": "dragon's_breath", "redstone": "redstone_dust",
    "bamboo_chest_raft": "bamboo_raft_with_chest", "experience_bottle": "bottle_o'_enchanting", "leather_chestplate": "leather_tunic", "leather_helmet": "leather_cap",
    "leather_leggings": "leather_pants"}
    notCapitalized = ["of", "with", "and"]
    filters = {"Favourites": item_filters.favourites_filter,"Armor Trims": item_filters.armor_trim_filter, "Smithing Templates": item_filters.smithing_template_filter, 
    "Pottery Sherds": item_filters.pottery_sherd_filter, "Spawn Eggs": item_filters.spawn_egg_filter, "Tools": item_filters.tools_filter,  "Armor": item_filters.armor_filter, 
    "Music Discs": item_filters.music_disc_filter, "Boats": item_filters.boats_filter, "Minecarts": item_filters.minecarts_filter, "Buckets": item_filters.buckets_filter}

    def __init__(self, filters, title, w, h, order_file="wiki_order.json", limit=-1, quit_function=lambda x: x, current_project=""):
        super().__init__()

        self.filters = filters
        self.search_filter = lambda x: True
        self.setWindowTitle(title)
        self.show()
        self.resize(w, h)
        self.quit_function = quit_function
        self.current_project = current_project
        self.vanilla = True
        self.blocks = False

        self.num_to_show = h//72 + 1
        self.start_index = 0

        self.checkboxes = []
        self.filterCheckboxes = []
        self.starBoxes = []
        self.favourites = []
        self.setButtons = []

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)

        self.mainLayout = QHBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)

        self.layout =  QFormLayout()

        self.leftWidget = QWidget()
        self.leftLayout = QFormLayout()
        self.leftWidget.setLayout(self.leftLayout)

        self.searchTools = QWidget()
        self.searchLayout = QHBoxLayout()
        self.searchTools.setLayout(self.searchLayout)

        self.searchBar = QLineEdit()
        self.searchLayout.addWidget(self.searchBar)
        
        self.limit = limit
        self.chosen = []
        self.chosenLabel = QLabel(f"0/{limit}")


        if self.limit != -1:
            self.searchLayout.addWidget(self.chosenLabel)

        self.finishedButton = QPushButton("Done")
        self.finishedButton.clicked.connect(self.return_values)
        self.finishedButton.setObjectName("hoverableButton")
        self.searchLayout.addWidget(self.finishedButton)

        self.leftLayout.addRow("Search:", self.searchTools)
        self.searchBar.textChanged.connect(self.update_display)

        self.items = []
        
        self.scrollArea = QScrollArea(self)
        self.scrollContent = QWidget(self.scrollArea)
        self.scrollContent.setObjectName("scroll")
        self.scrollContent.setLayout(self.layout)
        self.scrollArea.setWidgetResizable(True)
        self.order_file = QItemSelectorWindow.getOrderFile(order_file)
        self.scrollArea.verticalScrollBar().valueChanged.connect(self.handle_scroll)

        self.leftLayout.addRow(self.scrollArea)
        self.mainLayout.addWidget(self.leftWidget, 76)

        self.scrollArea.setWidget(self.scrollContent)
        self.scrollArea.setObjectName("scrollArea")

        self.settingsArea = QWidget()
        self.settingsLayout = QFormLayout()
        self.settingsArea.setLayout(self.settingsLayout)
        self.settingsArea.setObjectName("scroll")

        self.settingsScrollArea = QScrollArea()
        self.settingsScrollArea.setObjectName("scrollArea")
        self.settingsScrollArea.setWidgetResizable(True)
        self.settingsScrollArea.setWidget(self.settingsArea)
        self.mainLayout.addWidget(self.settingsScrollArea, 25)

        self.load_favourites()

        self.initialize_filters()
        self.initalize_sets()

        self.get_item_ids()
        self.initialize_items()

    @property
    def favourite_id(self):
        return "vanilla" if self.vanilla else self.current_project

    def handle_scroll(self):
        value = self.scrollArea.verticalScrollBar().value()
        new_start_value = value // 72
        if new_start_value > self.start_index:
            while self.start_index < new_start_value:
                self.add_new_item_below()
                self.start_index += 1

    def add_new_item_below(self):
        try:
            item = self.items[self.start_index + self.num_to_show - 1]
        except IndexError:
            return
        if self.blocks:
            self.add_block(item)
        else:
            self.add_item(item)


    def prepare_favourite_order(self):
        temp_file = self.order_file[:]
        for item in self.favourites[self.favourite_id]:
            temp_file.remove(item)
            temp_file.insert(0, item)
        return temp_file

    def load_favourites(self):
        with open("favourite.json", "r") as f:
            self.favourites = json.loads(f.read())

    def initialize_filters(self):
        filterHeading = QLabel("Filter Only...")
        filterHeading.setObjectName("itemGroupChoiceHeading")
        self.settingsLayout.addWidget(filterHeading)
        for filter_name in QItemSelectorWindow.filters.keys():
            checkWidget = QWidget()
            checkLayout = QHBoxLayout()
            checkWidget.setLayout(checkLayout)

            checkLayout.addWidget(QLabel(filter_name), 90)
            checkbox = QCheckBox()
            checkbox.setObjectName(filter_name)
            self.filterCheckboxes.append(checkbox)
            checkbox.toggled.connect(self.toggle_filter)
            checkLayout.addWidget(checkbox, 10)

            self.settingsLayout.addWidget(checkWidget)

    def initalize_sets(self):
        setHeading = QLabel("Item Sets")
        setHeading.setObjectName("itemGroupChoiceHeading")
        self.settingsLayout.addWidget(setHeading)

        vanillaItemsWidget = QWidget()
        vanillaItemsLayout = QHBoxLayout()
        vanillaItemsWidget.setLayout(vanillaItemsLayout)
        vanillaItemsLayout.addWidget(QLabel("Vanilla Items"), 90)
        vanillaRadioButton = QRadioButton()
        self.setButtons.append(vanillaRadioButton)
        vanillaItemsLayout.addWidget(vanillaRadioButton, 10)
        vanillaRadioButton.clicked.connect(lambda: self.toggle_set("vanilla_items"))

        vanillaBlocksWidget = QWidget()
        vanillaBlocksLayout = QHBoxLayout()
        vanillaBlocksWidget.setLayout(vanillaBlocksLayout)
        vanillaBlocksLayout.addWidget(QLabel("Vanilla Blocks"), 90)
        vanillaBlocksRadioButton = QRadioButton()
        self.setButtons.append(vanillaBlocksRadioButton)
        vanillaBlocksLayout.addWidget(vanillaBlocksRadioButton, 10)
        vanillaBlocksRadioButton.clicked.connect(lambda: self.toggle_set("vanilla_blocks"))

        if self.current_project != "":
            modItemsWidget = QWidget()
            modItemsLayout = QHBoxLayout()
            modItemsWidget.setLayout(modItemsLayout)
            modItemsLayout.addWidget(QLabel("Mod Items"), 90)
            modItemButton = QRadioButton()
            self.setButtons.append(modItemButton)
            modItemButton.clicked.connect(lambda: self.toggle_set("mod_items"))
            modItemsLayout.addWidget(modItemButton, 10)

            modBlocksWidget = QWidget()
            modBlocksLayout = QHBoxLayout()
            modBlocksWidget.setLayout(modBlocksLayout)
            modBlocksLayout.addWidget(QLabel("Mod Blocks"), 90)
            modBlockButton = QRadioButton()
            self.setButtons.append(modBlockButton)
            modBlockButton.clicked.connect(lambda: self.toggle_set("mod_blocks"))
            modBlocksLayout.addWidget(modBlockButton, 10)

        self.settingsLayout.addWidget(vanillaItemsWidget)
        self.settingsLayout.addWidget(vanillaBlocksWidget)
        self.settingsLayout.addWidget(modItemsWidget)
        self.settingsLayout.addWidget(modBlocksWidget)

    
    def toggle_set(self, value):
        if value == "vanilla_items":
            self.order_file = QItemSelectorWindow.getOrderFile("wiki_order.json")
            self.vanilla = True
            self.blocks = False
            for i in [1, 2, 3]:
                self.setButtons[i].setChecked(False)      
        elif value == "vanilla_blocks":
            self.vanilla = True
            self.blocks = True
            self.order_file = QItemSelectorWindow.getOrderFile("../block_orders/wiki_order_blocks.json")
            for i in [0, 2, 3]:
                self.setButtons[i].setChecked(False)
        elif value == "mod_items":
            self.vanilla = False
            self.blocks = False
            for i in [0, 1, 3]:
                self.setButtons[i].setChecked(False)
        elif value == "mod_blocks":
            self.vanilla = False
            self.blocks = True
            for i in [0, 1, 2]:
                self.setButtons[i].setChecked(False)
        self.update_display()


    def toggle_filter(self):
        self.filters.clear()
        for checkbox in self.filterCheckboxes:
            if checkbox.checkState() == 2:
                self.filters.append(QItemSelectorWindow.filters[checkbox.objectName()])
        if len(self.filters) == 0:
            self.filters.append(lambda x: True)
        self.update_display()

    def get_item_ids(self):
        self.items.clear()
        if self.vanilla:
            if not self.blocks:
                for item in self.prepare_favourite_order():
                    if True in [filter_function(item) for filter_function in self.filters] and self.search_filter(item):
                        self.items.append(item)
            else:
                for item in self.order_file:
                    if True in [filter_function(item) for filter_function in self.filters] and self.search_filter(item):
                            self.items.append(item)
        else:
            if not self.blocks:
                for item_file in os.listdir(f"{self.current_project}/items"):
                    with open(f"{self.current_project}/items/{item_file}") as f:
                        self.items.append(json.loads(f.read()))
            else:
                for item_file in os.listdir(f"{self.current_project}/blocks"):
                    with open(f"{self.current_project}/blocks/{item_file}") as f:
                        self.items.append(json.loads(f.read()))
        self.scrollContent.setFixedHeight(max(len(self.items) * 72, (self.num_to_show - 2)*72 - 36))

    def update_display(self):
        self.start_index = 0
        self.scrollArea.verticalScrollBar().setValue(0)
        self.search_filter = lambda x: x.startswith(self.searchBar.text())
        self.get_item_ids()
        self.clear_layout()
        self.initialize_items()

    def initialize_items(self):
        self.checkboxes.clear()
        self.starBoxes.clear()
        for item in self.items[self.start_index:self.start_index+self.num_to_show-1]:
            if self.vanilla:
                if not self.blocks:
                    self.add_item(item)
                else:
                    self.add_block(item)
            else:
                self.add_mod_item(item)

    def add_mod_item(self, item):
        name = item["name"]
        texture_file = item["texture"]
        item_id = item["id"]
        pixmap = QPixmap(texture_file)
        vanillaIcon = QVanillaItemIcon("redstone", (32, 32))
        vanillaIcon.set_pixmap(pixmap)
        self.add_item(item_id, vanillaIcon, name)

    def add_block(self, item):
        vanillaIcon = QVanillaItemIcon("redstone", (32, 32), False)
        vanillaIcon.set_block(item)
        self.add_item(item, vanillaIcon)

    def add_item(self, item, icon=None, itemName=""):
        itemRowWidget = QWidget()
        itemRow = QHBoxLayout()
        itemRowWidget.setLayout(itemRow)

        if icon is None:
            itemIcon = QVanillaItemIcon(item, (32, 32))
        else:
            itemIcon = icon
        if itemName == "":
            itemLabel = QLabel(QItemSelectorWindow.getItemNameFromID(item))
        else:
            itemLabel = QLabel(itemName)
        itemChosen = QCheckBox()
        itemChosen.setObjectName(item)
        self.checkboxes.append(itemChosen)
        if item in self.chosen:
            itemChosen.setChecked(True)
        itemChosen.toggled.connect(self.toggle_item)
        starButton = QPushButton()
        starButton.setObjectName(item)
        starButton.setCheckable(True)
        starButton.clicked.connect(self.toggle_favourites)
        if item not in self.favourites[self.favourite_id]:
            starButton.setStyleSheet(" border: none; padding: 0px; background-image: url('icons/star.png'); background-repeat: no-repeat; width: 30px; height: 30px; ")
        else:
            starButton.setStyleSheet(" border: none; padding: 0px; background-image: url('icons/fullStar.png'); background-repeat: no-repeat; width: 30px; height: 30px; ")
            starButton.setChecked(True)
        self.starBoxes.append(starButton)

        itemRow.addWidget(itemIcon, 5)
        itemRow.addWidget(itemLabel, 85)
        itemRow.addWidget(itemChosen, 5)
        itemRow.addWidget(starButton, 5)

        self.layout.addRow(itemRowWidget)

    def clear_layout(self):
        while self.layout.rowCount() > 0:
            self.layout.removeRow(0)

    def toggle_item(self):
        item_added = ""
        removed = False
        for checkbox in self.checkboxes:
            stem = "minecraft:" if self.vanilla else ""
            if checkbox.checkState() == 2:
                if stem + checkbox.objectName() not in self.chosen:
                    self.chosen.append(stem + checkbox.objectName())
                    item_added = stem + checkbox.objectName()
                    break
            elif stem + checkbox.objectName() in self.chosen:
                self.chosen.remove(stem + checkbox.objectName())
                removed = True
        if not removed and len(self.chosen) > self.limit and self.limit != -1:
            for checkbox in self.checkboxes:
                if checkbox.checkState() == 2 and checkbox.objectName() != item_added:
                    checkbox.setChecked(False)
                    break
            if len(self.chosen) > self.limit:
                self.chosen.remove(self.chosen[0])
        self.chosenLabel.setText(f"{len(self.chosen)}/{self.limit}")
        print(self.chosen)

    def toggle_favourites(self):
        for button in self.starBoxes:
            if button.isChecked() and button.objectName() not in self.favourites[self.favourite_id]:
                button.setStyleSheet(" border: none; padding: 0px; background-image: url('icons/fullStar.png'); background-repeat: no-repeat; width: 30px; height: 30px; ")
                self.favourites[self.favourite_id].append(button.objectName())
            elif not button.isChecked() and button.objectName() in self.favourites[self.favourite_id]:
                button.setStyleSheet(" border: none; padding: 0px; background-image: url('icons/star.png'); background-repeat: no-repeat; width: 30px; height: 30px; ")
                self.favourites[self.favourite_id].remove(button.objectName())
        self.save_favourites()
        self.load_favourites()


    def save_favourites(self):
        with open("favourite.json", "w") as f:
            f.write(json.dumps(self.favourites))


    def return_values(self):
        self.save_favourites()
        self.quit_function(self.chosen)
        self.destroy(True)


    @staticmethod
    def getItemNameFromID(itemID):
        IDToUse = itemID
        if itemID.endswith("_smithing_template"):
            IDToUse = IDToUse[:-18]
        if itemID.startswith("music_disc_"):
            disc_name = itemID[11:]
            IDToUse = f"music_disc_({disc_name.title()})"
        if itemID.endswith("_minecart"):
            IDToUse = f"minecart_with_{itemID[:-9]}"
        if itemID.endswith("_chest_boat"):
            IDToUse = f"{itemID[:-11]}_boat_with_chest"
        if itemID in QItemSelectorWindow.itemsToDifferentNames.keys():
            IDToUse = QItemSelectorWindow.itemsToDifferentNames[itemID]
        
        id_split = IDToUse.split("_")
        final_name = ""
        for part in id_split:
            if part not in QItemSelectorWindow.notCapitalized:
                part = part[0].upper() + part[1:]
            final_name += part + " "
        final_name = final_name[:-1]
        return final_name

    @staticmethod
    def getOrderFile(file):
        if file == "default_order":
            return QVanillaItemIcon.sprite_key.keys()
        with open(f"resources/item_orders/{file}") as f:
            return json.loads(f.read())["order"]
