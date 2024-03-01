from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, os
from  custom_highlighter import CustomHighlighter


class EditorWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.box_max_height = 400
        self.box_width = 800
        self.suggestion_shown = True
        self.selected_index = 0
        self.suggestion_height = 22
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
        self.box = QScrollArea(self)
        self.box.setFixedWidth(self.box_width)
        self.box.setMaximumHeight(self.box_max_height)

        self.box.setWidgetResizable(True)

        self.box_contents = QWidget(self)
        self.box_layout = QVBoxLayout()
        self.box_contents.setLayout(self.box_layout)
        self.box_contents.setObjectName("suggestionBox")
        self.box_layout.setSpacing(0)
        self.box_layout.setContentsMargins(0, 0, 0, 0)

        self.box.setWidget(self.box_contents)
        self.editor.installEventFilter(self)

        self.editor.cursorPositionChanged.connect(self.cursor_changed)
        self.editor.verticalScrollBar().valueChanged.connect(self.cursor_changed)

        self.set_suggestions([str(i) for i in range(100)])

        self.showMaximized()

    def eventFilter(self, widget, event):
        if event.type() != QEvent.KeyPress or not self.suggestion_shown:
            return False
        if event.key() == Qt.Key_Escape:
            self.editor.setFocus()
            self.suggestion_shown = False
            self.cursor_changed()
            return False
        elif event.key() == Qt.Key_Down:
            if self.selected_index < self.box_layout.count() - 1:
                self.selected_index += 1
                self.box_layout.itemAt(self.selected_index - 1).widget().setStyleSheet("background-color: transparent;")
                self.box_layout.itemAt(self.selected_index).widget().setStyleSheet("background-color: blue;")
            else:
                self.selected_index = 0
                self.box_layout.itemAt(self.box_layout.count() - 1).widget().setStyleSheet("background-color: transparent;")
                self.box_layout.itemAt(self.selected_index).widget().setStyleSheet("background-color: blue;")
            scroll_bar = self.box.verticalScrollBar()
            current_position = self.suggestion_height * self.selected_index
            if current_position > scroll_bar.value() + self.box.sizeHint().height() or current_position < scroll_bar.value():
                scroll_bar.setValue(current_position)
            return True
        elif event.key() == Qt.Key_Up :
            if self.selected_index > 0:
                self.selected_index -= 1
                self.box_layout.itemAt(self.selected_index + 1).widget().setStyleSheet("background-color: transparent;")
                self.box_layout.itemAt(self.selected_index).widget().setStyleSheet("background-color: blue;")
            else:
                self.selected_index = self.box_layout.count() - 1
                self.box_layout.itemAt(0).widget().setStyleSheet("background-color: transparent;")
                self.box_layout.itemAt(self.selected_index).widget().setStyleSheet("background-color: blue;")
            scroll_bar = self.box.verticalScrollBar()
            current_position = self.suggestion_height * self.selected_index
            if current_position > scroll_bar.value() + self.box.sizeHint().height() or current_position < scroll_bar.value():
                scroll_bar.setValue(current_position)
            return True
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.insert_text(self.box_layout.itemAt(self.selected_index).widget().text())
            return True
        
        return QWidget.eventFilter(self, widget, event)

    def insert_text(self, text, replace=False):
        if not replace:
            self.suggestion_shown = False
            self.cursor_changed()
            self.editor.textCursor().insertText(text)

    def cursor_changed(self):
        if self.suggestion_shown:
            self.box.show()
        else:
            self.box.hide()
            return
        self.cursorRect = self.editor.cursorRect()
        menu_height = self.menuBar().rect().height()
        line_height = QFontMetrics(self.font).height()
        self.box.move(max(self.cursorRect.x() - self.box_width, 4), self.cursorRect.y() + menu_height + line_height + 2)

    def set_suggestions(self, suggestions):
        for i in reversed(range(self.box_layout.count())):
            widget = self.box_layout.itemAt(i).widget()
            self.box_layout.removeWidget(widget)
        for i, suggestion in enumerate(suggestions):
            label = QLabel(suggestion)
            if i == 0:
                label.setStyleSheet("background-color: blue")
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            label.setFont(self.font)
            self.box_layout.addWidget(label)
        self.box.setFixedSize(self.box_width, min(self.box_max_height, self.box_contents.sizeHint().height() + 2))
        self.box.setFocusPolicy(Qt.NoFocus)

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
        self.editor.textChanged.connect(self.check)
        self.highlighter = CustomHighlighter(self.editor)

        self.editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editor.setLineWrapMode(QTextEdit.NoWrap)
        self.editor.setTabStopDistance(QFontMetricsF(self.editor.font()).horizontalAdvance(' ') * 8)
        self.editor.setFont(self.font)
        self.body.addWidget(self.editor)
        self.setCentralWidget(body_frame)
        self.editor.cursorPositionChanged.connect(self.reset_char_format)

    def open_file(self, path):
        self.editor.setText(open(path, "r").read())
        self.current_file = path

    def reset_char_format(self):
        self.editor.blockSignals(True)
        if self.editor.textCursor().selectionStart() == self.editor.textCursor().selectionEnd():
            self.editor.setCurrentCharFormat(self.highlighter.basicFormat)
        self.editor.blockSignals(False)

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
        reverse_brackets = {")": "(", "]": "[", "}": "{"}
        temp = self.editor.toPlainText()
        cursor: QTextCursor = self.editor.textCursor()
        cursor_pos = cursor.position()
        changed = False
        if len(self.old_text) == len(self.editor.toPlainText()) - 1:
            added = temp[cursor_pos-1]
            if added in brackets.keys():
                if cursor_pos == len(temp) or not temp[cursor_pos].isalnum():
                    self.editor.blockSignals(True)
                    scroll_pos = self.editor.verticalScrollBar().value()
                    self.editor.textCursor().insertText(brackets[added])
                    self.editor.verticalScrollBar().setValue(scroll_pos)
                    cursor.setPosition(cursor_pos)
                    self.editor.setTextCursor(cursor)
                    self.editor.blockSignals(False)
            elif added == "\n":
                current_line_index = cursor.blockNumber()
                lines = temp.split("\n")
                tab_count = self.getTabCount(lines[current_line_index], lines[current_line_index-1], cursor_pos)
                self.editor.blockSignals(True)
                self.editor.textCursor().insertText("\t"*tab_count)
                self.editor.blockSignals(False)
                if cursor_pos < len(temp) and temp[cursor_pos] in reverse_brackets.keys():
                    if cursor_pos > 1 and temp[cursor_pos-2] == reverse_brackets[temp[cursor_pos]]:
                        self.editor.blockSignals(True)
                        self.editor.textCursor().insertText("\n")
                        self.editor.textCursor().insertText("\t"*max(tab_count-1, 0))
                        temp_cursor = self.editor.textCursor()
                        temp_cursor.movePosition(QTextCursor.Up)
                        temp_cursor.movePosition(QTextCursor.EndOfLine)
                        self.editor.setTextCursor(temp_cursor)
                        self.editor.blockSignals(False)
                    else:
                        matching_index = EditorWindow.findBackwardsBracket(temp, cursor_pos, reverse_brackets[temp[cursor_pos]], temp[cursor_pos])
                        if matching_index is not None:
                            text = temp[matching_index:cursor_pos-1]
                            if "\n" not in text:
                                self.editor.blockSignals(True)
                                self.editor.textCursor().deletePreviousChar()
                                cursor = self.editor.textCursor()
                                cursor.setPosition(matching_index+1)
                                cursor.insertText("\n")
                                cursor.insertText("\t"*(tab_count))
                                cursor.movePosition(cursor.EndOfLine)
                                self.editor.setTextCursor(cursor)
                                self.editor.blockSignals(False)
        elif len(self.old_text) == len(self.editor.toPlainText()) + 1:
            removed = self.old_text[cursor_pos]
            if removed in brackets.keys():
                if cursor_pos < len(temp) and temp[cursor_pos] == brackets[removed]:
                    self.editor.blockSignals(True)
                    scroll_pos = self.editor.verticalScrollBar().value()
                    self.editor.textCursor().deleteChar()
                    self.editor.verticalScrollBar().setValue(scroll_pos)
                    cursor.setPosition(cursor_pos)
                    self.editor.setTextCursor(cursor)
                    self.editor.blockSignals(False)

        self.old_text = self.editor.toPlainText()

    def getTabCount(self, line, previous_line, index):
        previous_line = previous_line.expandtabs(2)
        prev_line_tab_no = (len(previous_line) - len(previous_line.strip(" ")))//2
        if previous_line.endswith(";") or (previous_line.strip(" ").startswith("@") and EditorWindow.getBracketNoOfLine(previous_line) == 0) or previous_line.endswith("]") or previous_line.endswith("}") \
            or previous_line.endswith(",") or previous_line.strip(" ").startswith("."):
            if previous_line.endswith(";") and previous_line.strip(" ").startswith("."):
                return prev_line_tab_no - 1
            return prev_line_tab_no
        elif previous_line.endswith(")"):
            raw_text = self.editor.toPlainText()
            matched = EditorWindow.findBackwardsBracket(raw_text, index-2)

            if matched is not None:
                char = "("
                isAnnotation = False
                while char != "\n" and matched > 0:
                    matched -= 1
                    char = raw_text[matched]
                    if char == "@":
                        isAnnotation = True
                        break

                if isAnnotation:
                    return prev_line_tab_no
                else:
                    return prev_line_tab_no + 1
        else:
            return prev_line_tab_no + 1

    @staticmethod
    def findBackwardsBracket(text, index, start="(", end=")"):
        bracket_no = 1
        while index > 0 and bracket_no > 0:
            index -= 1
            char = text[index]
            if char == start:
                bracket_no -= 1
            elif char == end:
                bracket_no += 1

        if bracket_no == 0:
            return index
        return None

    @staticmethod
    def getBracketNoOfLine(line, start="(", end=")"):
        bracket_no = 0
        for char in line:
            if char == start:
                bracket_no += 1
            elif char == end:
                bracket_no -= 1
        return bracket_no



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditorWindow()
    window.open_file("cool_minecraft_mod/custom_java/MetalDetectorItem.java")

    sys.exit(app.exec_())