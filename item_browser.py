from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFormLayout, QScrollArea, QMainWindow, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QCheckBox
from PyQt5.QtGui import QImage, QPixmap, QColor
import json


def get_sprite_key():
    with open("resources/spritekey.json") as f:
        return json.loads(f.read())


def get_spritesheet():
    with open("resources/spritesheet.json") as f:
        return json.loads(f.read())["img"]


class QVanillaItemIcon(QWidget):
    spritesheet = get_spritesheet()
    sprite_key  = get_sprite_key()

    def __init__(self, item_id, size, *args, **kwargs):
        super(QVanillaItemIcon, self).__init__(*args, **kwargs)

        self.item_id = item_id

        self.label = QLabel("")
        self.pixmap = QPixmap(16, 16)
        self.label.setPixmap(self.pixmap)
        self.size = size

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.label)
        self.setLayout(self.mainLayout)

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


class QItemSelectorWindow(QMainWindow):
    itemsToDifferentNames = \
    {"writable_book": "book_and_quill", "map": "empty_map", "filled_map": "map", "cooked_beef": "steak", "dragon_breath": "dragon's_breath", "redstone": "redstone_dust",
    "bamboo_chest_raft": "bamboo_raft_with_chest", "experience_bottle": "bottle_o'_enchanting"}
    notCapitalized = ["of", "with", "and"]
    name_to_order = {"Default Order": "defualt_order", "Wiki Order": "wiki_order.json"}

    def __init__(self, filter, title, w, h, order_file="wiki_order.json", limit=-1, quit_function=lambda x: x):
        super().__init__()

        self.filter = filter
        self.search_filter = lambda x: True
        self.setWindowTitle(title)
        self.show()
        self.resize(w, h)
        self.quit_function = quit_function

        self.checkboxes = []

        self.layout =  QFormLayout()

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
        self.searchLayout.addWidget(self.finishedButton)

        self.layout.addRow("Search:", self.searchTools)
        self.searchBar.textChanged.connect(self.update_display)

        self.items = []
        
        self.scrollArea = QScrollArea(self)
        self.scrollContent = QWidget(self.scrollArea)
        self.scrollContent.setLayout(self.layout)
        self.scrollArea.setWidgetResizable(True)
        self.order_file = QItemSelectorWindow.getOrderFile(order_file)

        self.setCentralWidget(self.scrollArea)

        self.scrollArea.setWidget(self.scrollContent)

        self.get_item_ids()
        self.initialize_items()


    def get_item_ids(self):
        self.items.clear()
        for item in self.order_file:
            if self.filter(item) and self.search_filter(item):
                self.items.append(item)

    def update_display(self):
        self.search_filter = lambda x: x.startswith(self.searchBar.text())
        self.get_item_ids()
        self.clear_layout()
        self.initialize_items()

    def initialize_items(self):
        for item in self.items:
            itemRow = QHBoxLayout()
            itemIcon = QVanillaItemIcon(item, (32, 32))
            itemLabel = QLabel(QItemSelectorWindow.getItemNameFromID(item))
            itemChosen = QCheckBox()
            itemChosen.setObjectName(item)
            self.checkboxes.append(itemChosen)
            itemChosen.toggled.connect(self.toggle_item)

            itemRow.addWidget(itemIcon, 5)
            itemRow.addWidget(itemLabel, 90)
            itemRow.addWidget(itemChosen, 5)

            self.layout.addRow(itemRow)

    def clear_layout(self):
        while self.layout.rowCount() > 1:
            self.layout.removeRow(1)

    def toggle_item(self):
        item_added = ""
        removed = False
        for checkbox in self.checkboxes:
            if checkbox.checkState() == 2:
                if checkbox.objectName() not in self.chosen:
                    self.chosen.append(checkbox.objectName())
                    item_added = checkbox.objectName()
            elif checkbox.objectName() in self.chosen:
                self.chosen.remove(checkbox.objectName())
                removed = True
        if not removed and len(self.chosen) > self.limit and self.limit != -1:
            for checkbox in self.checkboxes:
                if checkbox.checkState() == 2 and checkbox.objectName() != item_added:
                    checkbox.setChecked(False)
                    break
        print(item_added)
        self.chosenLabel.setText(f"{len(self.chosen)}/{self.limit}")

    def return_values(self):
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
