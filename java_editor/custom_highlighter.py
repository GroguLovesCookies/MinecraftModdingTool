from PyQt5.QtGui import *
import re


class CustomHighlighter:
    def __init__(self, document):
        self.document = document
        self.basicFormat = self.document.currentCharFormat()

        self.document.textChanged.connect(self.highlight)
        self.offset = 0
        self.current_line_count = self.document.document().blockCount()
        self.current_cursor_pos = self.document.textCursor().position()

    def highlightText(self, start, length, format, add_offset=True):
        self.document.blockSignals(True)

        scroll_pos = self.document.verticalScrollBar().value()

        cursor = self.document.textCursor()
        cursor_pos = cursor.position()
        if add_offset:
            cursor.setPosition(start + self.offset)
        else:
            cursor.setPosition(start)
        self.document.setTextCursor(cursor)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, length)
        self.document.setTextCursor(cursor)

        self.document.setCurrentCharFormat(format)
        cursor.setPosition(cursor_pos)
        self.document.setTextCursor(cursor)

        self.document.setCurrentCharFormat(self.basicFormat)

        self.document.verticalScrollBar().setValue(scroll_pos)

        self.document.blockSignals(False)

    def highlight(self, diff_on=False):
        self.document.setCurrentCharFormat(self.basicFormat)
        text, self.offset = self.get_total_line(diff_on)
        self.highlightTypes(text)
        self.highlightKeywords(text)
        self.highlightStrings(text)
        self.highlightAnnotations(text)
        self.highlightNumericals(text)
        self.highlightComments(text)
        self.highlightBrackets()

    def get_total_line(self, diff_on):
        new_line_count = self.document.document().blockCount()
        new_cursor_pos = self.document.textCursor().position()
        added_lines = new_line_count - self.current_line_count
        diff = self.current_cursor_pos - new_cursor_pos
        self.current_cursor_pos = new_cursor_pos
        self.current_line_count = new_line_count
        
        line = self.document.textCursor().blockNumber()
        raw_text = self.document.toPlainText()
        split = raw_text.split("\n")

        if diff == 0 and not diff_on:
            text_before = "\n".join(split[:line])
            text = split[line:line+added_lines]
        else:
            text_before = "\n".join(split[:line-added_lines])
            text = split[line-added_lines:line+1]
        text = "\n".join(text)
        if line == 0:
            return text, len(text_before)
        else:
            return text, len(text_before) + 1

    def highlightTypes(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setFontWeight(QFont.Bold)
        typeFormat.setForeground(QColor(219, 159, 103))

        pattern = "int|boolean|float|double|void"
        match = re.search(pattern, text)
        length = 0
        while match is not None and match.start() >= 0:
            if CustomHighlighter.isValidMatch(match, length, text):
                self.highlightText(match.start() + length, match.end()-match.start(), typeFormat)
            length += match.end() - match.start()
            match = re.search(pattern, text[length:])

    def highlightKeywords(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setFontWeight(QFont.Bold)
        typeFormat.setForeground(QColor(30, 104, 179))

        pattern = "public|private|protected|package|class|new|imports|true|false|this|import|if|else|continue|break|for|while|null"
        match = re.search(pattern, text)
        length = 0
        while match is not None and match.start() >= 0:
            if CustomHighlighter.isValidMatch(match, length, text):
                self.highlightText(match.start() + length, match.end()-match.start(), typeFormat)
            length += match.end() - match.start()
            match = re.search(pattern, text[length:])

    def highlightStrings(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setForeground(QColor(72, 156, 86))

        locations = CustomHighlighter.getStringLocations(text)
        for loc in locations:
            if len(loc) == 1:
                continue
            self.highlightText(loc[0], loc[1]-loc[0], typeFormat)
    
    def highlightAnnotations(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setForeground(QColor(144, 161, 63))

        pattern = "\@[a-zA-Z]+"
        match = re.search(pattern, text)
        length = 0
        while match is not None and match.start() >= 0:
            self.highlightText(match.start() + length, match.end()-match.start(), typeFormat)
            length += match.end() - match.start()
            match = re.search(pattern, text[length:])

    def highlightNumericals(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setForeground(QColor(61, 219, 161))

        pattern = "[0-9\.f]+"
        match = re.search(pattern, text)
        length = 0
        while match is not None and match.start() >= 0:
            if True in [str(i) in text[match.start() + length:match.end() + length] for i in range(10)]:
                self.highlightText(match.start() + length, match.end()-match.start(), typeFormat)
            length += match.end() - match.start()
            match = re.search(pattern, text[length:])

    def highlightComments(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setForeground(QColor(128, 128, 128))

        pattern = "\/\/.*"
        match = re.search(pattern, text)
        length = 0
        while match is not None and match.start() >= 0:
            self.highlightText(match.start() + length, match.end()-match.start(), typeFormat)
            length += match.end() - match.start()
            match = re.search(pattern, text[length:])

    def highlightBrackets(self):
        highlightableBrackets = {"(": ")", "[": "]", "{": "}"}
        reverseBrackets = {value: key for key, value in highlightableBrackets.items()}
        colors = [(107, 65, 148), (199, 192, 54), (141, 199, 154)]
        matches = {"(": 0, "[": 0, "{": 0}
        text = self.document.toPlainText()
        incorrectFormat = QTextCharFormat()
        incorrectFormat.setFontUnderline(True)
        incorrectFormat.setUnderlineColor(QColor(255, 0, 0))
        incorrectFormat.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)

        for i, char in enumerate(text):
            if char in highlightableBrackets.keys():
                if matches[char] < 0:
                    continue

                typeFormat = QTextCharFormat()
                typeFormat.setForeground(QColor(*colors[matches[char] % len(colors)]))
                end = self.find_matching_bracket(text, i, char, highlightableBrackets[char])
                if end == None:
                    self.highlightText(i, 1, incorrectFormat, False)
                    continue
                self.highlightText(i, 1, typeFormat, False)
                self.highlightText(end, 1, typeFormat, False)
                matches[char] += 1
            elif char in highlightableBrackets.values():
                matches[reverseBrackets[char]] -= 1

    @staticmethod
    def isValidMatch(match, length, text):
        return (match.start() + length == 0 or not text[match.start() + length - 1].isalnum()) \
            and (match.end() + length == len(text) or not text[match.end() + length].isalnum())

    @staticmethod
    def getStringLocations(text):
        i = 0
        inString = False
        stringLocs = []
        while i < len(text):
            char = text[i]
            if char == "\"" or char == "\'":
                if not inString:
                    inString = True
                    stringLocs.append([i])
                else:
                    inString = False
                    stringLocs[-1].append(i+1)
            i += 1
        return stringLocs

    def find_matching_bracket(self, text, index, start_char="(", end_char=")"):
        bracket_no = 1
        change = 1
        if text[index] == end_char:
            change = -1
        
        while index + change < len(text) and index + change >= 0 and bracket_no > 0:
            index += change
            char = text[index]
            if char == start_char:
                bracket_no += 1
            elif char == end_char:
                bracket_no -= 1

        if bracket_no == 0:
            return index
        else:   
            return None

    @staticmethod
    def find_nth_occurrence(string, sub_string, n):
        start_index = string.find(sub_string)
        while start_index >= 0 and n > 1:
            start_index = string.find(sub_string, start_index + 1)
            n -= 1
        return start_index
