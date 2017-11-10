from PyQt5.Qsci import QsciScintilla
from PyQt5.QtGui import (QFont, QFontMetrics, QColor)

from .KdbLexer import KdbLexer


class KdbCodeEditor(QsciScintilla):
    ARROW_MARKER_NUM = 8

    _file = None

    def __init__(self, parent=None, file=None):
        super(KdbCodeEditor, self).__init__(parent)

        self._file = file

        # Set the default font
        font = QFont()
        # font.setFamily('Courier')
        # font.setFixedPitch(True)
        # font.setPointSize(10)

        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        # self.connect(self,
        #     SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'),
        #     self.on_margin_clicked)
        self.markerDefine(QsciScintilla.RightArrow, self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor("#ee1111"), self.ARROW_MARKER_NUM)

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#fff4f4"))

        # Set Python lexer
        # Set style for Python comments (style number 1) to a fixed-width
        # courier.
        #
        lexer = KdbLexer(self)

        # lexer.keywords('in')

        self.setLexer(lexer)
        # self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # not too small
        # self.setMinimumSize(600, 450)

    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)

    def getFile(self):
        return self._file

    def setFile(self, file):
        self._file = file

    def save(self):
        print("Save file into {}".format(self._file))

        if self._file is not None:
            pass
        else:
            pass

    def load(self):
        pass
