from PyQt5.QtWidgets import QLineEdit

from KdbShape.kdb import ConnectionManager


class InstancesToolbarWidget(QLineEdit):
    def __init__(self, serversManager: ConnectionManager, parent=None):
        super(QLineEdit, self).__init__(parent)

        self.setFixedWidth(220)
        self.setMaximumWidth(200)

        self.serversManager = serversManager
        # self.serversManager.serverChanged.conect()

        self.returnPressed.connect(self.change_current_connection)

    def update_current_connection(self, uri):
        self.setText(uri)

    def change_current_connection(self):
        print(self.text())

        self.serversManager.change_instance(self.text())



        # > self.searchDBLine = QtGui.QLineEdit(self)
        # > self.searchDBLineAction = QtGui.QWidgetAction(self)
        # > self.searchDBLineAction.setDefaultWidget(self.searchDBLine)
        # > self.ui.toolBar.addAction(self.searchDBLineAction)
