from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, os
from syntax_highlighter import CustomHighlighter


class EditorWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.init_ui()

        self.current_file = None

    def init_ui(self):
        self.setWindowTitle("Editor")
        self.resize(1200, 800)

        self.font = QFont("Consolas")
        self.font.setPointSize(16)
        self.setFont(self.font)

        self.setStyleSheet(open(os.path.join(os.getcwd(), "qss/editor.qss"), "r").read())

        self.editor = None

        self.setup_menu()
        self.setup_main()

        self.showMaximized()

    def get_editor(self):
        pass

    def setup_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        open_file_action = file_menu.addAction("Open")
        open_file_action.setShortcut("Ctrl+O")
        # open_file_action.triggered.connect(self.open_file)

    def setup_main(self):
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.NoFrame)
        body_frame.setFrameShadow(QFrame.Plain)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.body = QHBoxLayout()
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(0)
        body_frame.setLayout(self.body)

        self.editor = QTextEdit()
        self.highlighter = CustomHighlighter(self.editor.document())
        self.editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editor.setFont(self.font)
        self.body.addWidget(self.editor)
        self.setCentralWidget(body_frame)

    def open_file(self, path):
        self.editor.setText(open(path, "r").read())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditorWindow()
    window.open_file("cool_minecraft_mod/custom_java/MetalDetectorItem.java")

    sys.exit(app.exec_())