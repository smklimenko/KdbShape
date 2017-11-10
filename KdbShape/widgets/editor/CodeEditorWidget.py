import re

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget)

from .KdbCodeEditor import KdbCodeEditor

_TAB_PREFIX = "New"


class CodeEditorWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabPosition(QTabWidget.North)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)

    def createBlankEditor(self):
        tab = KdbCodeEditor()

        # self.tabs
        self.tabs.addTab(tab, self._get_next_tab_name())

    def saveCurrentEditor(self):
        self.tabs.currentWidget().save()

    def _get_next_tab_name(self):
        p = re.compile(_TAB_PREFIX + "([0-9]+)")

        index = 0
        for i in range(self.tabs.count()):
            m = p.match(self.tabs.tabText(i))
            index = max(0, 0 if m is None else int(m.group(1)))

        return _TAB_PREFIX + str(index + 1)
