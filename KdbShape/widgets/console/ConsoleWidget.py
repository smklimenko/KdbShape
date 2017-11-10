from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton


class ConsoleWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Initialize tab screen
        self.tabs = QTabWidget()
        # self.tabs.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.tabs.setMovable(True)
        self.tabs.setTabPosition(QTabWidget.South)

        self.tab1 = QWidget()
        self.tab1.setContentsMargins(0, 0, 0, 0)

        self.tab2 = QWidget()
        self.tab2.setContentsMargins(0, 0, 0, 0)

        # self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "Console")
        self.tabs.addTab(self.tab2, "Result")

        # # Create first tab
        # self.tab1.layout = QVBoxLayout(self)
        # self.pushButton1 = QPushButton("PyQt5 button")
        # self.tab1.layout.addWidget(self.pushButton1)
        # self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
