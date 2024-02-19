import os
import json
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QLabel, QLineEdit, QWidget, QSizePolicy, QCheckBox
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QPixmap
from form import QForm, QFilePathBox, QItemBrowseBox
import shutil
from item_browser import QItemSelectorWindow
from creation_windows.item_group_creator_window import ItemGroupCreatorWindow
from creation_windows.item_creator_window import ItemCreatorWindow
from creation_windows.block_creator_window import BlockCreatorWindow
from creation_windows.recipe_creator_window import RecipeCreatorWindow


def create_new_item_group(menuWindow, current_project, path=""):
    menuWindow.hide()
    return initialize_item_group_creator_window(current_project, path)


def initialize_item_group_creator_window(current_project, path=""):
    itemGroupCreatorWindow = ItemGroupCreatorWindow("Create New Item Group", 1200, 800, 0, 0, current_project, path)
    return itemGroupCreatorWindow


def create_new_item(menuWindow, current_project):
    menuWindow.hide()
    return initialize_item_creator_window(current_project)


def initialize_item_creator_window(current_project):
    itemCreatorWindow = ItemCreatorWindow("Create New Item", 1200, 800, 200, 100, current_project)
    return itemCreatorWindow


def create_new_block(menuWindow, current_project):
    menuWindow.hide()
    return initialize_block_creator_window(current_project)


def initialize_block_creator_window(current_project):
    return BlockCreatorWindow("Create New Block", 1200, 800, 200, 100, current_project)


def create_new_recipe(menuWindow, current_project):
    menuWindow.hide()
    return initialize_recipe_creator_window(current_project)


def initialize_recipe_creator_window(current_project):
    return RecipeCreatorWindow("Create New Recipe", 1200, 800, 200, 200, current_project)