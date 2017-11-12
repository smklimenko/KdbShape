import re

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QIcon


class QPadItem(object):
    def __init__(self, name, uri=None, sid=None, parent=None):
        self.uri = uri
        self.sid = sid
        self.itemName = name

        self.parentItem = parent
        self.childItems = []

        if parent is not None:
            parent.childItems.append(self)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 1

    def match(self, pattern):
        if self.sid:
            return re.match(pattern, self.sid, flags=re.I) is not None

        for c in self.childItems:
            if c.match(pattern):
                return True
        return False

    def data(self, uri_hidden):
        return self.itemName if self.uri is None or uri_hidden else self.itemName + " (`" + self.uri + ")"

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0


class QPadTreeModel(QAbstractItemModel):

    def __init__(self, source, parent=None):
        super(QPadTreeModel, self).__init__(parent)

        self.QWE = QIcon(':/images/print.png')
        self.__FOLDER_ICON = QIcon(':/images/folder.svg')

        self.roots = []
        self.uriHidden = False

        self.modelSource = source

        self.reload_items()

    def save_items(self):
        pass

    def reload_items(self):
        with open(self.modelSource) as f:
            data = f.read().splitlines()

        nodes = {}
        self.roots = []

        for sid in data:
            sid = sid.strip()[1:]  # first is always empty

            path = ''
            parent = None
            tokens = sid.split('`')
            name_length = len(tokens) - 2
            for i, name in enumerate(tokens[1:]):
                path += name
                node = nodes.get(path)
                if node is None:
                    if i == name_length:
                        node = QPadItem(name, sid=sid, uri=tokens[0], parent=parent)
                    else:
                        node = QPadItem(name, parent=parent)
                    nodes[path] = node
                    if parent is None:
                        self.roots.append(node)
                parent = node

    def getUriHidden(self):
        return self.uriHidden

    def setUriHidden(self, hidden):
        self.uriHidden = hidden

    def headerData(self, section, orientation, role):
        return None

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return 1

    def filtered(self, index, pattern):
        if not index.isValid():
            return False
        return index.internalPointer().match(pattern)

    def data(self, index, role):
        if not index.isValid():
            return None

        p = index.internalPointer()
        if role == Qt.DisplayRole:
            return p.data(self.uriHidden)

        if role == Qt.DecorationRole:
            return self.__FOLDER_ICON if p.sid is None else self.QWE

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        # if orientation == Qt.Horizontal and role == Qt.DisplayRole:
        #     return self.rootItem.data(section)
        #
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, self.roots[row])

        child = parent.internalPointer().child(row)
        if child:
            return self.createIndex(row, column, child)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        parent = index.internalPointer().parent()
        if not parent:  # root node
            return QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            return len(self.roots)
        else:
            return parent.internalPointer().childCount()
