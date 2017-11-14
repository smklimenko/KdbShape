import os

import appdirs
from PyQt5.QtCore import QObject, pyqtSignal

from KdbShape import APPLICATION_NAME
from KdbShape.widgets.server.QPadTreeModel import QPadTreeModel
from KdbShape.widgets.server.ServersTreeWidget import ServersTreeWidget


class ServersViewManager(QObject):
    __spots__ = ['widgets']
    serverChanged = pyqtSignal(['QString'])

    def __init__(self):
        super(QObject, self).__init__()

        self.widgets = []

    def create_server_widgets(self, parent=None):
        try:
            p = appdirs.user_data_dir(APPLICATION_NAME + "/cons", appauthor=False, roaming=True)
            files = {name for name in os.listdir(p) if name.lower().endswith(".srv")}
            for f in files:
                name = f[:-4]

                model = QPadTreeModel(os.path.join(p, f))
                model.setUriHidden(False)

                widget = ServersTreeWidget(name, model, parent)
                widget.setObjectName("ServerView-" + name)

                self.widgets.append(widget)
        except FileNotFoundError as e:
            pass

        return self.widgets

    def get_server_widgets(self):
        return self.widgets

    def change_current_server(self, uri):
        print("ServerView: sever changed to" + uri)
        self.serverChanged.emit(uri)

        #
        # def asd(self):
        #     model = QPadTreeModel(f, self)
        #     model.setUriHidden(False)
        #
        #     f = os.path.join(, name + ".srv")
