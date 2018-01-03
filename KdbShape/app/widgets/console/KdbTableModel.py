from PyQt5.QtCore import Qt, QAbstractTableModel


class KdbTableModel(QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """

    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)

        # self.console.setRowCount(len(r))
        # self.console.setColumnCount(len(r.dtype.names))
        # self.console.setHorizontalHeaderLabels(r.dtype.names)
        #
        # for i, row in enumerate(r):
        #     for j, cell in enumerate(row):
        #         self.console.setItem(i, j, QTableWidgetItem(str(r[i][j])))

        self._data = data
        self.r = len(data)
        self.c = len(data.dtype.codes)

    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.dtype.codes[section]
            elif orientation == Qt.Vertical:
                return section
        return None
