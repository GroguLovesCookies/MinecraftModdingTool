from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import re


class CustomHighlighter(QSyntaxHighlighter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def highlightBlock(self, text):
        self.highlightTypes(text)
        self.highlightKeywords(text)
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
