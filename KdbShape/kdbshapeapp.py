import datetime

from PyQt5.QtCore import QFile, Qt, QTextStream, QSettings, QDirIterator
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import (QKeySequence, QTextCursor)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (QDialog, QDockWidget, QFileDialog, QMessageBox)
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction

from KdbShape import APPLICATION_NAME
from KdbShape.widgets.console.ConsoleWidget import ConsoleWidget
from KdbShape.widgets.editor.CodeEditorWidget import CodeEditorWidget
from KdbShape.widgets.server.ServersViewManager import ServersListManager
import KdbShape.kdbshapeapp_rc


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.connection = None

        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "asd", "settings")
        self.settings.setFallbacksEnabled(False)

        self._restore_state()

        self.codeEditor = CodeEditorWidget(self)
        self.setCentralWidget(self.codeEditor)

        # Create Tree widget
        self.serversViewManager = ServersListManager()
        for w in self.serversViewManager.reload_servers_widgets():
            w.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            self.addDockWidget(Qt.LeftDockWidgetArea, w)

            # self.serversTree = ServersTreeWidget(self, "Mock1")
        #
        # dock = QDockWidget("Mock1", self)
        # dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # dock.setWidget(self.serversTree)
        # self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        # self.load_servers_widgets()

        # Create console widget
        self.console = ConsoleWidget(self)

        dock = QDockWidget("Console", self)
        dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        dock.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

        # self.console.setReadOnly(True)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        # self.createDockWindows()

        self.setWindowTitle(APPLICATION_NAME)

        # self.newLetter()

        # def newLetter(self):
        # self.textEdit.clear()
        #
        # cursor = self.textEdit.textCursor()
        # cursor.movePosition(QTextCursor.Start)
        # topFrame = cursor.currentFrame()
        # topFrameFormat = topFrame.frameFormat()
        # topFrameFormat.setPadding(16)
        # topFrame.setFrameFormat(topFrameFormat)
        #
        # textFormat = QTextCharFormat()
        # boldFormat = QTextCharFormat()
        # boldFormat.setFontWeight(QFont.Bold)
        # italicFormat = QTextCharFormat()
        # italicFormat.setFontItalic(True)
        #
        # tableFormat = QTextTableFormat()
        # tableFormat.setBorder(1)
        # tableFormat.setCellPadding(16)
        # tableFormat.setAlignment(Qt.AlignRight)
        # cursor.insertTable(1, 1, tableFormat)
        # cursor.insertText("The Firm", boldFormat)
        # cursor.insertBlock()
        # cursor.insertText("321 City Street", textFormat)
        # cursor.insertBlock()
        # cursor.insertText("Industry Park")
        # cursor.insertBlock()
        # cursor.insertText("Some Country")
        # cursor.setPosition(topFrame.lastPosition())
        # cursor.insertText(QDate.currentDate().toString("d MMMM yyyy"),
        #         textFormat)
        # cursor.insertBlock()
        # cursor.insertBlock()
        # cursor.insertText("Dear ", textFormat)
        # cursor.insertText("NAME", italicFormat)
        # cursor.insertText(",", textFormat)
        # for i in range(3):
        #     cursor.insertBlock()
        # cursor.insertText("Yours sincerely,", textFormat)
        # for i in range(3):
        #     cursor.insertBlock()
        # cursor.insertText("The Boss", textFormat)
        # cursor.insertBlock()
        # cursor.insertText("ADDRESS", italicFormat)

        # def load_servers_widgets(self):

        # self.serversTree = ServersTreeWidget(self, "Mock1")
        #
        # dock = QDockWidget("Mock1", self)
        # dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # dock.setWidget(self.serversTree)
        # self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _restore_state(self):
        if self.settings.value("windowState") is not None:
            self.restoreState(self.settings.value("windowState"))

        if self.settings.value("geometry") is not None:
            self.restoreGeometry(self.settings.value("geometry"))

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        event.accept()

    def execute(self):
        if self.connection is None:
            pass

        s = self.codeEditor.text(self.codeEditor.getCursorPosition()[0]).strip()
        print(datetime.datetime.now())
        r = self.connection(s, raw=True)
        # r = self.connection(s)
        print(datetime.datetime.now())

        print("Done")
        # self.console.clear()
        # self.console.setModel(QTableModel(r))
        # self.console.setRowCount(len(r))
        # self.console.setColumnCount(len(r.dtype.names))
        # self.console.setHorizontalHeaderLabels(r.dtype.names)
        #
        # for i, row in enumerate(r):
        #     for j, cell in enumerate(row):
        #         self.console.setItem(i, j, QTableWidgetItem(str(r[i][j])))


        # self.console.setItem(0, 0, QTableWidgetItem("Cell (1,1)"))
        # self.console.setItem(0, 1, QTableWidgetItem("Cell (1,2)"))
        # self.console.setItem(1, 0, QTableWidgetItem("Cell (2,1)"))
        # self.console.setItem(1, 1, QTableWidgetItem("Cell (2,2)"))
        # self.console.setItem(2, 0, QTableWidgetItem("Cell (3,1)"))
        # self.console.setItem(2, 1, QTableWidgetItem("Cell (3,2)"))
        # self.console.setItem(3, 0, QTableWidgetItem("Cell (4,1)"))
        # self.console.setItem(3, 1, QTableWidgetItem("Cell (4,2)"))
        # self.console.move(0, 0)
        # self.console.textCursor().insertText(str(r))

    def print_(self):
        document = self.codeEditor.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        document.print_(printer)

        self.statusBar().showMessage("Ready", 2000)

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self,
                                                  "Choose a file name", '.', "HTML (*.html *.htm)")
        if not filename:
            return

        file = QFile(filename)
        if not file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self, "Dock Widgets",
                                "Cannot write file %s:\n%s." % (filename, file.errorString()))
            return

        out = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        out << self.codeEditor.toHtml()
        QApplication.restoreOverrideCursor()

        self.statusBar().showMessage("Saved '%s'" % filename, 2000)

    def undo(self):
        document = self.codeEditor.document()
        document.undo()

    def insertCustomer(self, customer):
        if not customer:
            return
        customerList = customer.split(', ')
        document = self.codeEditor.document()
        cursor = document.find('NAME')
        if not cursor.isNull():
            cursor.beginEditBlock()
            cursor.insertText(customerList[0])
            oldcursor = cursor
            cursor = document.find('ADDRESS')
            if not cursor.isNull():
                for i in customerList[1:]:
                    cursor.insertBlock()
                    cursor.insertText(i)
                cursor.endEditBlock()
            else:
                oldcursor.endEditBlock()

    def addParagraph(self, paragraph):
        if not paragraph:
            return
        document = self.codeEditor.document()
        cursor = document.find("Yours sincerely,")
        if cursor.isNull():
            return
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.PreviousBlock, QTextCursor.MoveAnchor,
                            2)
        cursor.insertBlock()
        cursor.insertText(paragraph)
        cursor.insertBlock()
        cursor.endEditBlock()

    def about(self):
        QMessageBox.about(self, "About Dock Widgets",
                          "The <b>Dock Widgets</b> example demonstrates how to use "
                          "Qt's dock widgets. You can enter your own text, click a "
                          "customer to add a customer name and address, and click "
                          "standard paragraphs to add them.")

    def createActions(self):
        self.createBlankFile = QAction(QIcon(':/images/new.png'), "&New", self,
                                       shortcut=QKeySequence(Qt.CTRL + Qt.Key_N),
                                       statusTip="Create new shape", triggered=self.codeEditor.createBlankEditor)
        # self.newLetterAct = QAction(QIcon(':/images/new.png'), "&New Letter",
        #         self, shortcut=QKeySequence.New,
        #         statusTip="Create a new form letter", triggered=self.newLetter)

        self.executeLine = QAction(QIcon(':/images/save.png'), "&Execute", self,
                                   shortcut=QKeySequence(Qt.CTRL + Qt.Key_Enter),
                                   statusTip="Execute current line", triggered=self.execute)

        self.saveAct = QAction(QIcon(':/images/save.png'), "&Save...", self,
                               shortcut=QKeySequence.Save,
                               statusTip="Save the current form letter", triggered=self.save)

        self.printAct = QAction(QIcon(':/images/print.png'), "&Print...", self,
                                shortcut=QKeySequence.Print,
                                statusTip="Print the current form letter",
                                triggered=self.print_)

        self.undoAct = QAction(QIcon(':/images/undo.png'), "&Undo", self,
                               shortcut=QKeySequence.Undo,
                               statusTip="Undo the last editing action", triggered=self.undo)

        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q",
                               statusTip="Quit the application", triggered=self.close)

        self.aboutAct = QAction("&About", self,
                                statusTip="Show the application's About box",
                                triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                                  statusTip="Show the Qt library's About box",
                                  triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.createBlankFile)
        self.fileMenu.addAction(self.executeLine)
        # self.fileMenu.addAction(self.saveAct)
        # self.fileMenu.addAction(self.printAct)
        # self.fileMenu.addSeparator()
        # self.fileMenu.addAction(self.quitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        # self.editMenu.addAction(self.undoAct)

        self.viewMenu = self.menuBar().addMenu("&View")

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        # self.helpMenu.addAction(self.aboutAct)
        # self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        # self.fileToolBar.addAction(self.newLetterAct)
        # self.fileToolBar.addAction(self.saveAct)
        # self.fileToolBar.addAction(self.printAct)

        self.editToolBar = self.addToolBar("Edit")
        # self.editToolBar.addAction(self.undoAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")


if __name__ == '__main__':
    import sys

    try:
        app = QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
