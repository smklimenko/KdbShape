from KdbShape.widgets.server.InstancesTreeModel import InstancesTreeModel, InstancesFilteringModel
from PyQt5.QtCore import QMargins, Qt, QSettings, QItemSelectionModel
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAbstractItemView, QWidget, QVBoxLayout, QLineEdit, QMenu, QInputDialog)
from PyQt5.QtWidgets import QTreeView
from qtpy import QtCore, QtWidgets

from KdbShape.app.widgets.server.storage.QPadModelSerializer import QPadModelSerializer


class InstancesTreeWidget(QWidget):
    def __init__(self, descriptor, parent=None):
        QWidget.__init__(self, parent)

        self.descriptor = descriptor

        self.instancesModel = InstancesTreeModel()
        QPadModelSerializer(self.descriptor.file).load_model(self.instancesModel)

        self.instancesModel.dataChanged.connect(self.__store_model)
        self.instancesModel.rowsInserted.connect(self.__store_model)
        self.instancesModel.rowsMoved.connect(self.__store_model)
        self.instancesModel.rowsRemoved.connect(self.__store_model)

        proxy = InstancesFilteringModel(self.instancesModel)

        fil = QLineEdit(self)
        fil.textChanged.connect(proxy.setSearchText)

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

        layout.addWidget(fil)
        layout.addWidget(self.treeView)

        self.setLayout(layout)

    def __store_model(self):
        QPadModelSerializer(self.descriptor.file).save_model(self.instancesModel)

    def __change_active_server(self, index):
        print("Changed by double click: " + str(index))


        # print(index.data(Qt.DisplayRole))

        # item = self.treeView.model().itemFromIndex(index)
        # print(item)

    def __open_context_menu(self, position):
        menu = QMenu()

        index = self.treeView.indexAt(position)

        create_menu = menu.addMenu("Create")
        create_menu.addAction(QIcon(':/images/editor/new_file.png'), "Instance").triggered.connect(
            self.__action_create_instance(index))

        create_menu.addAction(QIcon(':/images/editor/new_folder.png'), "Directory").triggered.connect(
            self.__action_create_folder(index))

        menu.addSeparator()
        menu.addAction(self.tr("Connect"))
        menu.addAction(self.tr("Disconnect"))
        menu.addSeparator()
        menu.addAction(self.tr("Edit Instance"))
        menu.addAction(self.tr("Clone Instance"))
        menu.addSeparator()
        menu.addAction(self.tr("Delete"))

        menu.exec_(self.treeView.viewport().mapToGlobal(position))

    def __action_create_instance(self, index):
        def closure():
            reply = QInputDialog.getText(self, 'New Folder', "Folder name:")

            if not reply[1]:
                return False

            proxy = self.treeView.model()
            idx = proxy.mapFromSource(
                self.instancesModel.insertInstance(reply[0], "`:" + reply[0] + ":123123", -1, proxy.mapToSource(index)))
            sel = self.treeView.selectionModel()
            sel.setCurrentIndex(idx, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)

            return True

        return closure

    def __action_create_folder(self, index):
        def closure():
            reply = QInputDialog.getText(self, 'New Folder', "Folder name:")

            if not reply[1]:
                return False

            proxy = self.treeView.model()
            idx = proxy.mapFromSource(self.instancesModel.insertFolder(reply[0], -1, proxy.mapToSource(index)))
            sel = self.treeView.selectionModel()
            sel.setCurrentIndex(idx, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)

            return True

        return closure

    def store_state(self, settings: QSettings):
        v = self.treeView
        exp = []
        for i in v.model().persistentIndexList():
            if v.isExpanded(i):
                exp.append(i.data(Qt.UserRole))
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
