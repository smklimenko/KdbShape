from builtins import property

from PyQt5.QtCore import QMargins, QSortFilterProxyModel, Qt, QSettings
from PyQt5.QtGui import QIcon
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

        self._name = name

        self.treeView = QTreeView(self)

        self.treeView.setModel(myProxy)

        self.treeView.setHeaderHidden(True)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.__open_context_menu)
        self.treeView.doubleClicked.connect(self.__change_active_server)

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

    @property
    def name(self):
        return self._name

    def __change_active_server(self, index):
        print("Changed by double click")
        print(index.data(Qt.DisplayRole))

        # item = self.treeView.model().itemFromIndex(index)
        # print(item)

    def __open_context_menu(self, position):
        menu = QMenu()

        create_menu = menu.addMenu("Create")
        create_menu.addAction(QIcon(':/images/editor/new_file.png'), "Instance").triggered.connect(
            self.create_instance_action)
        create_menu.addAction(QIcon(':/images/editor/new_folder.png'), "Directory").triggered.connect(
            self.create_dir_action)

        menu.addSeparator()
        menu.addAction(self.tr("Connect"))
        menu.addAction(self.tr("Disconnect"))
        menu.addSeparator()
        menu.addAction(self.tr("Edit Instance"))
        menu.addAction(self.tr("Clone Instance"))
        menu.addSeparator()
        menu.addAction(self.tr("Delete"))

        menu.exec_(self.treeView.viewport().mapToGlobal(position))

    def create_dir_action(self):
        print("create_dir_action")
        pass

    def create_instance_action(self):
        print("Create instance")
        pass

    def store_state(self, settings: QSettings):
        v = self.treeView
        exp = []
        for i in v.model().persistentIndexList():
            if v.isExpanded(i):
                exp.append(i.data(Qt.UserRole))
        print(exp)
        settings.setValue("ExpandedItems", exp)

    def restore_state(self, settings: QSettings):
        items = settings.value("ExpandedItems", [])
        if not items:
            return

        v = self.treeView
        m = v.model()
        for item in items:
            idx = m.match(m.index(0, 0), Qt.UserRole, item, flags=Qt.MatchExactly | Qt.MatchRecursive)
            for i in idx:
                v.setExpanded(i, True)
