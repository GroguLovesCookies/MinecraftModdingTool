from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import sys


def create_new_project(self):
    print("New Project Created")


def open_new_project(self):
    print("Open Project")


if __name__ == "__main__":
    menu_buttons = []

    app = QApplication(sys.argv)

    window = QWidget()
    window.resize(1200, 800)
    window.setWindowTitle("New Project")
    window.show()

    windowParent = QWidget(window)
    windowParent.resize(600, 600)
    windowParent.show()

    windowLayout = QVBoxLayout(windowParent)
    windowParent.setLayout(windowLayout)

    windowParent.move(window.width()//2 - windowParent.width()//2, window.height()//2 - windowParent.height()//2)

    new_button = QPushButton("+ New Project", window)
    new_button.clicked.connect(create_new_project)
    windowLayout.addWidget(new_button, 2)
    menu_buttons.append(new_button)

    open_button = QPushButton("Open Project", window)
    open_button.clicked.connect(create_new_project)
    windowLayout.addWidget(open_button, 2)
    menu_buttons.append(open_button)

    for button in menu_buttons:
        button.setFixedHeight(600//len(menu_buttons) - 10)

    sys.exit(app.exec_())