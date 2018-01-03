from PyQt5.Qsci import *
from PyQt5.QtGui import *

from  KdbShape.app.widgets.editor.KdbParser import *


class KdbLexer(QsciLexerCustom):
    parser = KdbParser()

    def __init__(self, parent):
        super(KdbLexer, self).__init__(parent)

        font = QFont("Consolas", 8)

        bold_font = QFont(font)
        bold_font.setBold(True)

        self.setDefaultFont(font)
        self.setAutoIndentStyle(True)

        for c in KdbStyle.const, KdbStyle.type_guid, KdbStyle.type_float, KdbStyle.type_int:
            self.setColor(QColor("#3368ff"), c)

        for c in KdbStyle.type_datetime, KdbStyle.type_time, KdbStyle.type_date:
            self.setColor(QColor("#3368ff"), c)

        self.setColor(QColor("#b30086"), KdbStyle.sym)

        for c in KdbStyle.keyword_language, KdbStyle.command:
            self.setColor(QColor("#f0b400"), c)

        # KdbStyle.keyword_operator - operators are black
        for c in KdbStyle.keyword_function, KdbStyle.keyword_control:
            self.setFont(bold_font, c)
            self.setColor(QColor("#0000ff"), c)

        for c in KdbStyle.name, KdbStyle.variable:
            self.setColor(QColor("#b4a000"), c)

        self.setColor(QColor("#808080"), KdbStyle.comment)

        self.setColor(QColor("#14c800"), KdbStyle.string)

    def language(self):
        return "KDB+ Language"

    def description(self, style):
        if KdbStyle.has_value(style):
            return "kdb_style_" + KdbStyle(style).name
        return ""

    def styleText(self, start, end):
        self.startStyling(0)

        txt = self.parent().__test_current()
        for r in self.parser.invalidate(txt, 0, len(txt)):
            self.setStyling(len(r.token.encode("utf-8")), r.style)
