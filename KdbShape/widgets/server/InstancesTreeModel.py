import re

from PyQt5.QtCore import QAbstractItemModel, Qt, QModelIndex
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

        #
        # def create_folder(self, name, index=-1):
        #     if self.__uri:
        #         raise ValueError
        #
        #     item = InstanceItem(name)
        #
        #     self.__children.append(item)
        #     item.__parent = self
        #     item.__path = self.__path + "`" + name
        #
        #     return item
        #
        # def create_instance(self, name, uri, index=-1):
        #     if self.__uri:
        #         raise ValueError
        #
        #     item = InstanceItem(name, uri)
        #
        #     self.__children.append(item)
        #     item.__parent = self
        #     item.__path = self.__path + "`" + name
        #
        #     return item
        #
        # def discard(self):
        #     self.__parent.remove(self)
        #
        # def parent(self):
        #     return self.__parent
        #
        # def get_index(self):
        #     if self.__parent:
        #         return self.__parent.__children.index(self)
        #     return 0
        #
        # def child_by_row(self, row):
        #     return self.__children[row]
        #
        # def child_by_name(self, name):
        #     return next((c for c in self.__children if c.__name == name), None)
        #
        # def children_count(self):
        #     return len(self.__children)
        #
        # def is_active(self):
        #     return self.__active
        #
        # def is_folder(self):
        #     return self.__uri is None
        #
        # def is_instance(self):
        #     return self.__uri is not None
        #
        # def get_display_name(self, show_uri):
        #     if show_uri and self.__uri:
        #         return self.__name + " (" + self.__uri + ")"
        #     return self.__name
        #


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
        #
        # def get_item(self, index) -> Optional[TreeItem]:
        #     if index.isValid():
        #         item = index.internalPointer()
        #         if item:
        #             return item
        #     return self.rootItem
        #
        # def insert_instance(self, name, uri, parent=QModelIndex()):
        #     return self.__append_item(TreeItem(name, uri), parent)
        #
        # def append_directory(self, name, parent=QModelIndex()):
        #     return self.__append_item(TreeItem(name), parent)
        #
        # def __append_item(self, item, parent):
        #     parent_item = self.get_item(parent)
        #
        #     size = parent_item.count()
        #     if parent_item:
        #         self.beginInsertRows(parent, size, size + 1)
        #         parent_item.append_item(item)
        #         self.endInsertRows()
        #         parent.sibling(size + 1, 0)
        #         return self.index(size, 0)
        #     return parent
        #
        # def remove_item(self, index):
        #     pass
        #
        # # Inheritance
        # def columnCount(self, parent):
        #     return 1
        #
        # def data(self, index, role):
        #
        # def flags(self, index):
        #     if not index.isValid():
        #         return Qt.NoItemFlags
        #
        #     return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        #
        # def headerData(self, section, orientation, role=0):
        #     return None
        #
        # def index(self, row, column, parent=QModelIndex()):
        #     if not self.hasIndex(row, column, parent):
        #         return QModelIndex()
        #
        #     if not parent.isValid():
        #         parent_item = self.rootItem
        #     else:
        #         parent_item = parent.internalPointer()
        #
        #     child_item = parent_item.child_by_row(row)
        #     if child_item:
        #         return self.createIndex(row, column, child_item)
        #     else:
        #         return QModelIndex()
        #
        # def parent(self, index):
        #     if not index.isValid():
        #         return QModelIndex()
        #
        #     child_item = index.internalPointer()
        #     parent_item = child_item.parent()
        #
        #     if parent_item == self.rootItem:
        #         return QModelIndex()
        #
        #     return self.createIndex(parent_item.get_index(), 0, parent_item)
        #
        # def rowCount(self, parent=QModelIndex()):
        #     if parent.column() > 0:
        #         return 0
        #
        #     if not parent.isValid():
        #         parent_item = self.rootItem
        #     else:
        #         parent_item = parent.internalPointer()
        #
        #     return parent_item.children_count()
