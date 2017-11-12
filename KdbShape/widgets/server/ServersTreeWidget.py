from PyQt5.QtCore import QMargins, QSortFilterProxyModel, Qt
from PyQt5.QtWidgets import (QAbstractItemView, QDockWidget, QWidget, QVBoxLayout, QLineEdit, QMenu)
from PyQt5.QtWidgets import QTreeView
from qtpy import QtCore, QtWidgets


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

        rexp = self.searchText.split(" ")
        for i, r in enumerate(rexp):
            rexp[i] = "(?=.*(" + r + "))"
        return sourceModel.filtered(indexProc, "^" + "".join(rexp) + ".*$")


class ServersTreeWidget(QDockWidget):
    def __init__(self, name, model, parent=None):
        QDockWidget.__init__(self, name, parent)

        myProxy = MyProxyModel()
        myProxy.setSourceModel(model)
        # myProxy.setFilterRegExp(".*")

        fil = QLineEdit(self)
        fil.textChanged.connect(myProxy.setSearchText)

        self.treeView = QTreeView(self)

        self.treeView.setModel(myProxy)

        self.treeView.setHeaderHidden(True)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.open_context_menu)

        header = self.treeView.header()
        header.setStretchLastSection(False)
        header.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))

        widget = QWidget()
        widget.setLayout(layout)

        self.setWidget(widget)

        layout.addWidget(fil)
        layout.addWidget(self.treeView)

    def open_context_menu(self, position):
        level = 0
        indexes = self.treeView.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QMenu()
        if level == 0:
            menu.addAction(self.tr("Create folder"))
            menu.addAction(self.tr("Remove the folder"))
            menu.addAction(self.tr("Create New Server"))
        elif level == 1:
            menu.addAction(self.tr("Edit Server"))
            menu.addAction(self.tr("Remove Server"))
        elif level == 2:
            menu.addAction(self.tr("Edit object"))

        menu.exec_(self.treeView.viewport().mapToGlobal(position))
