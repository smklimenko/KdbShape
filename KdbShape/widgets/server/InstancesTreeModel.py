import re

from PyQt5.QtCore import QAbstractItemModel, Qt, QModelIndex, QSortFilterProxyModel
from PyQt5.QtGui import QIcon, QFont


class TreeItem:
    __slots__ = ("__name", "__path", "__uri", "__active", "__parent", "__children")

    def __init__(self, name, uri=None):
        self.__uri = uri
        self.__name = name
        self.__path = name

        self.__parent = None
        self.__children = []

        self.__active = False

    def parent(self):
        return self.__parent

    def children(self):
        return self.__children

    def child(self, row):
        return self.__children[row]

    def childByName(self, name):
        return next((c for c in self.__children if c.__name == name), None)

    def childCount(self):
        return len(self.__children)

    def childNumber(self):
        if self.__parent is not None:
            return self.__parent.__children.index(self)
        return 0

    def insertChildren(self, position, item):
        if position < 0 or position > len(self.__children):
            return False

        item.__parent = self
        item.__path = self.__path + "`" + item.__name

        self.__children.insert(position, item)

        return True

    def removeChildren(self, position, count):
        if position < 0 or position + count > len(self.__children):
            return False

        for row in range(count):
            self.__children.pop(position)

        return True

    def getName(self):
        return self.__name

    def getUri(self):
        return self.__uri

    def getPath(self):
        return self.__path

    def isActive(self):
        return self.__active

    def isInstance(self):
        return self.__uri is not None

    def setName(self, name):
        self.__name = name

    def setActive(self, active):
        self.__active = active

    def filter_accepts_item(self, pattern):
        pa = re.match(pattern, self.__path, flags=re.I)
        if pa:
            return True

        if self.__uri:
            return re.match(pattern, self.__uri, flags=re.I)

        for c in self.__children:
            if c.filter_accepts_item(pattern):
                return True
        return False


class InstancesFilteringModel(QSortFilterProxyModel):
    def __init__(self, source_model):
        super(InstancesFilteringModel, self).__init__()
        self.searchPattern = None
        self.setSourceModel(source_model)

    def setSearchText(self, arg=None):
        if arg:
            r = self.searchPattern.split(" ")
            for i, r in enumerate(r):
                r[i] = "(?=.*(" + r + "))"
            self.searchPattern = "^" + "".join(r) + ".*$"
        else:
            self.searchPattern = None
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        if not self.searchPattern:
            return True

        model = self.sourceModel()
        idx = model.index(row, 0, parent)

        return model.filter_accepts_row(idx, self.searchPattern)


class InstancesTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(InstancesTreeModel, self).__init__(parent)

        self.rootItem = TreeItem("")
        self.showInstanceUri = True

        self.__FOLDER_ICON = QIcon(':/images/server/folder.png')

        self.__ITEM_DEFAULT_ICON = QIcon(':/images/server/server_default.png')
        self.__ITEM_SELECTED_ICON = QIcon(':/images/server/server_selected.png')

        self.__ACTIVE_INSTANCE_FOND = QFont()
        self.__ACTIVE_INSTANCE_FOND.setBold(True)

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role=-1):
        if not index.isValid():
            return None

        p = self.getItem(index)
        if role == Qt.EditRole:
            return p.getName()

        if role == Qt.DisplayRole:
            return p.getName() + " (" + p.getUri() + ")" if self.showInstanceUri and p.isInstance() else p.getName()

        if role == Qt.FontRole and p.isActive():
            return self.__ACTIVE_INSTANCE_FOND

        if role == Qt.DecorationRole:
            if p.isInstance():
                return self.__ITEM_SELECTED_ICON if p.isActive() else self.__ITEM_DEFAULT_ICON
            return self.__FOLDER_ICON

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.rootItem

    def findByName(self, index: QModelIndex, name: str) -> QModelIndex:
        item = index.internalPointer() if index.isValid() else self.rootItem

        found = item.childByName(name)
        if found:
            return self.createIndex(found.childNumber(), 0, found)
        return QModelIndex()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        return None

    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        return False

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()

        childItem = self.getItem(index)
        parentItem = childItem.parent()
        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.childNumber(), 0, parentItem)

    def insertFolder(self, name: str, position: int, parent=QModelIndex()):
        return self.__insertItem(TreeItem(name), position, parent)

    def insertInstance(self, name: str, uri: str, position: int, parent=QModelIndex()):
        return self.__insertItem(TreeItem(name, uri), position, parent)

    def __insertItem(self, item: TreeItem, position: int, parent: QModelIndex) -> QModelIndex:
        parentItem = self.getItem(parent)

        pos = 1 + parentItem.childCount() + position if position < 0 else position

        self.beginInsertRows(parent, pos, pos)
        success = parentItem.insertChildren(pos, item)
        self.endInsertRows()

        return self.createIndex(pos, 0, item) if success else QModelIndex()

    def removeItems(self, position: int, rows: int, parent=QModelIndex()):
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parentItem.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent=QModelIndex()):
        parentItem = self.getItem(parent)
        return parentItem.childCount()

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False

        self.getItem(index).setName(value)
        self.dataChanged.emit(index, index)

        return True

    @staticmethod
    def filter_accepts_row(index, pattern):
        if not index.isValid():
            return False
        return index.internalPointer().filter_accepts_item(pattern)
