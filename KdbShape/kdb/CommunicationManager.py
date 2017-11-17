from PyQt5.QtCore import QObject, pyqtSignal


class CommunicationManager(QObject):
    __spots__ = []  # ['widgets']
    serverChanged = pyqtSignal(['QString'])

    def __init__(self):
        super(QObject, self).__init__()


    def change_instance(self, uri):
        print("ServerView: sever changed to" + uri)
        self.serverChanged.emit(uri)

        #
        # def asd(self):
        #     model = QPadTreeModel(f, self)
        #     model.setUriHidden(False)
        #
        #     f = os.path.join(, name + ".srv")
