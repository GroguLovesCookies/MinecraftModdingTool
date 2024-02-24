from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import re


class CustomHighlighter(QSyntaxHighlighter):
    def __init__(self, editor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editor = editor


    def highlightBlock(self, text):
        self.highlightTypes(text)
        self.highlightKeywords(text)
        self.highlightBrackets(text)
        self.highlightStrings(text)
        self.highlightAnnotations(text)
        self.highlightNumericals(text)
        self.highlightComments(text)

    
    def highlightTypes(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setFontWeight(QFont.Bold)
        typeFormat.setForeground(QColor(219, 159, 103))

        pattern = "int|boolean|float|double|void"
        match = re.search(pattern, text)
        length = 0
        while match is not None and match.start() >= 0:
            if CustomHighlighter.isValidMatch(match, length, text):
                self.setFormat(match.start() + length, match.end()-match.start(), typeFormat)
            length += match.end() - match.start()
            match = re.search(pattern, text[length:])

    def highlightKeywords(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setFontWeight(QFont.Bold)
        typeFormat.setForeground(QColor(30, 104, 179))

        pattern = "public|private|protected|package|class|new|imports|true|false|this|import|if|else|continue|break"
        match = re.search(pattern, text)
        length = 0
        while match is not None and match.start() >= 0:
            if CustomHighlighter.isValidMatch(match, length, text):
                self.setFormat(match.start() + length, match.end()-match.start(), typeFormat)
            length += match.end() - match.start()
            match = re.search(pattern, text[length:])

    def highlightStrings(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setForeground(QColor(72, 156, 86))

        locations = CustomHighlighter.getStringLocations(text)
        for loc in locations:
            if len(loc) == 1:
                continue
            self.setFormat(loc[0], loc[1]-loc[0], typeFormat)

    def highlightAnnotations(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setForeground(QColor(144, 161, 63))

        pattern = "\@[a-zA-Z]+"
        match = re.search(pattern, text)
        length = 0
        while match is not None and match.start() >= 0:
            self.setFormat(match.start() + length, match.end()-match.start(), typeFormat)
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
                self.setFormat(match.start() + length, match.end()-match.start(), typeFormat)
            length += match.end() - match.start()
            match = re.search(pattern, text[length:])

    def highlightComments(self, text):
        typeFormat = QTextCharFormat()
        typeFormat.setForeground(QColor(128, 128, 128))

        pattern = "\/\/.*"
        match = re.search(pattern, text)
        length = 0
        while match is not None and match.start() >= 0:
            self.setFormat(match.start() + length, match.end()-match.start(), typeFormat)
            length += match.end() - match.start()
            match = re.search(pattern, text[length:])

    def highlightBrackets(self, text):
        colors = [(107, 65, 148), (199, 192, 54), (141, 199, 154)]
        matches = 0
        incorrectFormat = QTextCharFormat()
        incorrectFormat.setFontUnderline(True)
        incorrectFormat.setUnderlineColor(QColor(255, 0, 0))
        incorrectFormat.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)

        for i, char in enumerate(text):
            if char == "(":
                if matches < 0:
                    continue

                typeFormat = QTextCharFormat()
                typeFormat.setForeground(QColor(*colors[matches % len(colors)]))
                end = CustomHighlighter.find_matching_bracket(text, i)
                if end == None:
                    self.setFormat(i, 1, incorrectFormat)
                    continue
                self.setFormat(i, 1, typeFormat)
                self.setFormat(end, 1, typeFormat)
                matches += 1
            elif char == ")":
                matches -= 1

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

    @staticmethod
    def find_matching_bracket(text, index):
        bracket_no = 1
        change = 1
        if text[index] == ")":
            change = -1
        
        while index + change < len(text) and index + change >= 0 and bracket_no > 0:
            index += change
            char = text[index]
            if char == "(":
                bracket_no += 1
            elif char == ")":
                bracket_no -= 1

        if bracket_no == 0:
            return index
        else:
            return None
