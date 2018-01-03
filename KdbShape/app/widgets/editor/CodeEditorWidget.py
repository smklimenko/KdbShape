import os
import re

import appdirs
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget)

from KdbShape import APPLICATION_NAME
from .KdbCodeEditor import KdbCodeEditor


class CodeEditorWidget(QWidget):
    __TAB_PREFIX = "New"

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

        self.__restore_editors()

    def __restore_editors(self):
        try:
            p = appdirs.user_data_dir(APPLICATION_NAME + "/tabs", appauthor=False, roaming=True)
            os.makedirs(p, exist_ok=True)
            files = {name for name in os.listdir(p) if name.lower().endswith(".q")}
            for name in files:
                file = os.path.join(p, name)

                tab = KdbCodeEditor(file)
                self.tabs.addTab(tab, name[:-2])

                # self.__create_widget(InstancesDescriptor(name, f))
        finally:
            pass

    def createBlankEditor(self):
        tab = KdbCodeEditor()

        # self.tabs
        self.tabs.addTab(tab, self._get_next_tab_name())

    def saveCurrentEditor(self):
        self.tabs.currentWidget().save()

    def _get_next_tab_name(self):
        p = re.compile(CodeEditorWidget.__TAB_PREFIX + "([0-9]+)")

        index = 0
        for i in range(self.tabs.count()):
            m = p.match(self.tabs.tabText(i))
            index = max(0, 0 if m is None else int(m.group(1)))

        return CodeEditorWidget.__TAB_PREFIX + str(index + 1)
