from PyQt5.QtCore import QMargins, QSortFilterProxyModel, Qt
from PyQt5.QtWidgets import (QAbstractItemView, QDockWidget, QWidget, QVBoxLayout, QLineEdit)
from PyQt5.QtWidgets import QTreeView


class MyProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super(MyProxyModel, self).__init__()
        self.searchText = None

    def setSearchText(self, arg=None):
        self.searchText = arg
        self.invalidateFilter()

    def filterAcceptsRow(self, rowProc, parentProc):
        if not self.searchText:
            return True

        sourceModel = self.sourceModel()
        indexProc = sourceModel.index(rowProc, 0, parentProc)

        nodeName = sourceModel.data(indexProc, Qt.DisplayRole)

        if nodeName and not str(self.searchText).lower() in nodeName.lower():
            return False
        return True


class ServersTreeWidget(QDockWidget):
    def __init__(self, name, model, parent=None):
        QDockWidget.__init__(self, name, parent)

        myProxy = MyProxyModel()
        myProxy.setSourceModel(model)
        # myProxy.setFilterRegExp(".*")

        fil = QLineEdit(self)
        fil.textChanged.connect(myProxy.setSearchText)

        view = QTreeView(self)

        view.setModel(myProxy)

        view.setHeaderHidden(True)
        view.setUniformRowHeights(True)
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))

        widget = QWidget()
        widget.setLayout(layout)

        self.setWidget(widget)

        layout.addWidget(fil)
        layout.addWidget(view)
