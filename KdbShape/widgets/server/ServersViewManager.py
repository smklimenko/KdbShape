import os

import appdirs

from KdbShape import APPLICATION_NAME
from KdbShape.widgets.server.QPadTreeModel import QPadTreeModel
from KdbShape.widgets.server.ServersTreeWidget import ServersTreeWidget


class ServersListManager:
    def __init__(self):
        self.widgets = []

    def reload_servers_widgets(self):
        try:
            p = appdirs.user_data_dir(APPLICATION_NAME, appauthor=False, roaming=True)
            files = {name for name in os.listdir(p) if name.lower().endswith(".srv")}
            for f in files:
                model = QPadTreeModel(os.path.join(p, f))
                model.setUriHidden(False)

                self.widgets.append(ServersTreeWidget(f[:-4], model))
        except FileNotFoundError as e:
            pass

        return self.widgets
        #
        # def asd(self):
        #     model = QPadTreeModel(f, self)
        #     model.setUriHidden(False)
        #
        #     f = os.path.join(, name + ".srv")
