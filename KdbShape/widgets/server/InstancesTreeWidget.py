import collections
from builtins import property

from PyQt5.QtCore import QMargins, QSortFilterProxyModel, Qt, QSettings, QItemSelectionModel
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAbstractItemView, QDockWidget, QWidget, QVBoxLayout, QLineEdit, QMenu, QInputDialog)
from PyQt5.QtWidgets import QTreeView
from qtpy import QtCore, QtWidgets

from KdbShape.widgets.server.InstancesTreeModel import InstancesTreeModel

InstancesDescriptor = collections.namedtuple("InstancesDescriptor", "name serializer")


class InstancesFilteringModel(QSortFilterProxyModel):
    def __init__(self):
        super(InstancesFilteringModel, self).__init__()
        self.searchText = None

    def set_search_text(self, arg=None):
        self.searchText = arg
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        if not self.searchText:
            return True

        model = self.sourceModel()
        idx = model.index(row, 0, parent)

        r = self.searchText.split(" ")
        for i, r in enumerate(r):
            r[i] = "(?=.*(" + r + "))"
        return model.filter_accepts_row(idx, "^" + "".join(r) + ".*$")


class InstancesTreeWidget(QDockWidget):
    def __init__(self, descriptor: InstancesDescriptor, parent=None):
        QDockWidget.__init__(self, descriptor.name, parent)

        self.descriptor = descriptor
        self.setObjectName(descriptor.name)

        self.instancesModel = InstancesTreeModel()
        self.descriptor.serializer.load_model(self.instancesModel)

        self.instancesModel.dataChanged.connect(self.__store_model)
        self.instancesModel.rowsInserted.connect(self.__store_model)
        self.instancesModel.rowsMoved.connect(self.__store_model)
        self.instancesModel.rowsRemoved.connect(self.__store_model)

        proxy = InstancesFilteringModel()
        proxy.setSourceModel(self.instancesModel)

        fil = QLineEdit(self)
        fil.textChanged.connect(proxy.set_search_text)

        self.treeView = QTreeView(self)

        self.treeView.setModel(proxy)

        self.treeView.setHeaderHidden(True)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.doubleClicked.connect(self.__change_active_server)
        self.treeView.customContextMenuRequested.connect(self.__open_context_menu)

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

    def __store_model(self):
        self.descriptor.serializer.save_model(self.instancesModel)

    def __change_active_server(self, index):
        print("Changed by double click: " + str(index))


        # print(index.data(Qt.DisplayRole))

        # item = self.treeView.model().itemFromIndex(index)
        # print(item)

    def __open_context_menu(self, position):
        menu = QMenu()

        create_menu = menu.addMenu("Create")
        create_menu.addAction(QIcon(':/images/editor/new_file.png'), "Instance").triggered.connect(
            self.__action_create_instance)

        create_menu.addAction(QIcon(':/images/editor/new_folder.png'), "Directory").triggered.connect(
            self.__action_create_folder)

        menu.addSeparator()
        menu.addAction(self.tr("Connect"))
        menu.addAction(self.tr("Disconnect"))
        menu.addSeparator()
        menu.addAction(self.tr("Edit Instance"))
        menu.addAction(self.tr("Clone Instance"))
        menu.addSeparator()
        menu.addAction(self.tr("Delete"))

        menu.exec_(self.treeView.viewport().mapToGlobal(position))

    def __action_create_instance(self):
        print("Create instance")
        pass

    def __action_create_folder(self):
        reply = QInputDialog.getText(self, 'New Folder', "Folder name:")

        if not reply[1]:
            return False

        sel = self.treeView.selectionModel()
        idx = sel.currentIndex()
        if not idx.isValid():
            return False

        proxy = self.treeView.model()

        idx = proxy.mapFromSource(self.instancesModel.insertFolder(reply[0], -1, proxy.mapToSource(idx)))

        sel.setCurrentIndex(idx, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)

        return True

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
