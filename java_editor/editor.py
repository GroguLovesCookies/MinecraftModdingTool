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

        self.current_file = ""

    def init_ui(self):
        self.setWindowTitle("Editor")
        self.resize(1200, 800)

        self.font = QFont("Consolas")
        self.font.setPointSize(16)
        self.setFont(self.font)

        self.setStyleSheet(open(os.path.join(os.getcwd(), "qss/editor.qss"), "r").read())

        self.editor = None

        self.setup_main()
        self.setup_menu()

        self.old_text = ""

        self.showMaximized()

    def setup_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        open_file_action = file_menu.addAction("Open")
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.triggered.connect(self.open_file_menu)

        save_file_action = file_menu.addAction("Save")
        save_file_action.setShortcut("Ctrl+S")
        save_file_action.triggered.connect(self.save_file)

        edit_menu = menu_bar.addMenu("Edit")

        open_file_action = file_menu.addAction("Undo")
        open_file_action.setShortcut("Ctrl+Z")
        open_file_action.triggered.connect(self.editor.undo)

        save_file_action = file_menu.addAction("Redo")
        save_file_action.setShortcut("Ctrl+Shift+Z")
        save_file_action.triggered.connect(self.editor.redo)

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
        self.highlighter = CustomHighlighter(self.editor, self.editor.document())
        self.editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editor.setLineWrapMode(QTextEdit.NoWrap)
        self.editor.setTabStopDistance(QFontMetricsF(self.editor.font()).horizontalAdvance(' ') * 16)
        self.editor.setFont(self.font)
        self.body.addWidget(self.editor)
        self.setCentralWidget(body_frame)
        self.editor.textChanged.connect(self.check)

    def open_file(self, path):
        self.editor.setText(open(path, "r").read())
        self.current_file = path

    def open_file_menu(self):
        path = QFileDialog.getOpenFileName(self, "Open File", os.getcwd())
        self.open_file(path[0])

    def save_file(self):
        if self.current_file != "" and os.path.isfile(self.current_file):
            with open(self.current_file, "w") as f:
                f.write(self.editor.toPlainText())

    def check(self):
        self.check_brackets()

    def check_brackets(self):
        brackets = {"(": ")", "[": "]", "{": "}", "\"": "\"", "'": "'"}
        temp = self.editor.toPlainText()
        cursor: QTextCursor = self.editor.textCursor()
        cursor_pos = cursor.position()
        changed = False
        if len(self.old_text) == len(self.editor.toPlainText()) - 1:
            changed = True
            added = temp[cursor_pos-1]
            if added in brackets.keys():
                if cursor_pos == len(temp) or not temp[cursor_pos].isalnum():
                    listed = list(temp)
                    listed.insert(cursor_pos, brackets[added])
                    temp = "".join(listed)
        elif len(self.old_text) == len(self.editor.toPlainText()) + 1:
            changed = True
            removed = self.old_text[cursor_pos]
            if removed in brackets.keys():
                if temp[cursor_pos] == brackets[removed]:
                    listed = list(temp)
                    listed.pop(cursor_pos)
                    temp = "".join(listed)

        if changed:
            self.old_text = ""
            scroll_pos = self.editor.verticalScrollBar().value()
            self.editor.setText(temp)
            self.editor.verticalScrollBar().setValue(scroll_pos)
            cursor.setPosition(cursor_pos)
            self.editor.setTextCursor(cursor)
        self.old_text = temp    



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditorWindow()
    window.open_file("cool_minecraft_mod/custom_java/MetalDetectorItem.java")

    sys.exit(app.exec_())