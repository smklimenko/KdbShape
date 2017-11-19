import collections
import os

import appdirs
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QTabWidget

from KdbShape import APPLICATION_NAME
from KdbShape.widgets.server.InstancesTreeWidget import InstancesTreeWidget

InstancesDescriptor = collections.namedtuple("InstancesDescriptor", "name file")


class InstancesWidget(QTabWidget):
    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent)

        self.instanceViews = {}

        self.setMovable(True)
        self.setTabPosition(QTabWidget.South)

        self.__load_tree_widgets()

        if not self.count():
            self.createInstanceView("Default")

    def __load_tree_widgets(self):
        try:
            p = appdirs.user_data_dir(APPLICATION_NAME + "/insts", appauthor=False, roaming=True)
            os.makedirs(p, exist_ok=True)
            # files = {name for name in os.listdir(p) if name.lower().endswith(".qp")}

            files = os.listdir(p)
            for f in files:
                name, ext = os.path.splitext(f)
                if ext[0] == '.':
                    ext = ext[1:].lower()

                f = os.path.join(p, f)
                self.__create_widget(InstancesDescriptor(name, f))
        finally:
            pass

    def createInstanceView(self, name):
        p = appdirs.user_data_dir(APPLICATION_NAME + "/insts", appauthor=False, roaming=True)
        os.makedirs(p, exist_ok=True)

        f = os.path.join(p, name + ".json")
        open(f, 'a').close()

        self.__create_widget(InstancesDescriptor(name, f))

    def removeInstancesView(self, name):
        pass

    def __create_widget(self, descriptor):
        widget = InstancesTreeWidget(descriptor, self)
        self.addTab(widget, descriptor.name)

    def store_state(self, settings: QSettings):
        pass

    def restore_state(self, settings: QSettings):
        pass
