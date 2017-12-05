import datetime

from PyQt5.QtCore import Qt, QSettings, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import (QKeySequence)
from PyQt5.QtWidgets import (QDockWidget, QWidgetAction, QInputDialog)
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction

from KdbShape import APPLICATION_NAME
from KdbShape.kdb.CommunicationManager import CommunicationManager
from KdbShape.widgets.console.ConsoleWidget import ConsoleWidget
from KdbShape.widgets.editor.CodeEditorWidget import CodeEditorWidget
from KdbShape.widgets.server.InstancesToolbarWidget import InstancesToolbarWidget
from KdbShape.widgets.server.InstancesWidget import InstancesWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(APPLICATION_NAME)

        self.communicationManager = CommunicationManager()

        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, APPLICATION_NAME, "windows")
        self.settings.setFallbacksEnabled(False)

        self.__create_instances()

        self.__create_code_editor()

        self.__create_console()

        self.__create_actions()

        self.__create_menus()

        self.__create_toolbars()

        self.__create_statusbar()

        self.__restore_state()

    def __create_instances(self):
        self.instances = InstancesWidget()

        dock = QDockWidget("Instances", self)
        dock.setObjectName("Instances")
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(self.instances)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def __create_code_editor(self):
        self.codeEditor = CodeEditorWidget(self)
        self.setCentralWidget(self.codeEditor)

    def __create_console(self):
        # Create console widget
        self.console = ConsoleWidget(self)

        dock = QDockWidget("Console", self)
        dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        dock.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def __execute_line(self):
        if self.connection is None:
            pass

        s = self.codeEditor.text(self.codeEditor.getCursorPosition()[0]).strip()
        print(datetime.datetime.now())
        r = self.connection(s, raw=True)
        # r = self.connection(s)
        print(datetime.datetime.now())

        print("Done")

    def undo(self):
        document = self.codeEditor.document()
        document.undo()

    def __create_actions(self):
        self.actionCreateFile = QAction(QIcon(':/images/editor/new_file.png'), "&New", self,
                                        shortcut=QKeySequence(Qt.CTRL + Qt.Key_N),
                                        statusTip="Create new shape", triggered=self.codeEditor.createBlankEditor)

        self.actionExecuteLine = QAction(QIcon(':/images/editor/save.png'), "&Execute", self,
                                         shortcut=QKeySequence(Qt.CTRL + Qt.Key_Enter),
                                         statusTip="Execute current line", triggered=self.__execute_line)

        # self.actionCreateInstancesView = QAction(QIcon(':/images/save.png'), "&Execute", self,
        #                                  shortcut=QKeySequence(Qt.CTRL + Qt.Key_Enter),
        #                                  statusTip="Execute current line", triggered=self.__execute_line)

    def __create_menus(self):
        file = self.menuBar().addMenu("&File")
        file.addAction(self.actionCreateFile)
        file.addAction("&Open")
        file.addAction("Save as..")
        recent = file.addMenu("Open &Recent")
        file.addSeparator()
        file.addAction("Se&ttings...", self.__mock_action, shortcut=QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_S))
        file.addSeparator()
        file.addAction("E&xit").triggered.connect(QCoreApplication.quit)

        inst = self.menuBar().addMenu("&Instance")
        inst.addAction(QIcon(':/images/server/folder.png'), "&Create View").triggered.connect(
            self.__create_instances_view)
        inst.addAction(QIcon(':/images/server/folder.png'), "&Delete View").triggered.connect(
            self.__delete_instances_view)
        inst.addSeparator()
        inst.addAction("Create Folder")
        inst.addAction("Create Instance")
        inst.addAction("Delete")
        inst.addSeparator()
        inst.addAction("Edit Instance")
        inst.addAction("Clone Instance")

        run = self.menuBar().addMenu("&Run")
        run.addAction(self.actionExecuteLine)

        # self.editMenu = self.menuBar().addMenu("&Edit")
        #
        # self.viewMenu = self.menuBar().addMenu("&View")
        #
        # self.menuBar().addSeparator()
        #
        # self.helpMenu = self.menuBar().addMenu("&Help")

    def __create_instances_view(self):
        name = QInputDialog.getText(self, 'Instances View Name', "Create New Instances View:")
        if name[1]:
            self.instances.createInstanceView(name[0])

    def __mock_action(self):
        print("Mock action called")

    def __delete_instances_view(self):
        pass

    def __create_toolbars(self):
        server_change_action = QWidgetAction(self)
        server_change_action.setDefaultWidget(InstancesToolbarWidget(self.communicationManager, self))

        self.toolbar = self.addToolBar("General")
        self.toolbar.addAction(server_change_action)

    def __create_statusbar(self):
        self.statusBar().showMessage("Ready")

    def closeEvent(self, event):
        self.__store_state()
        event.accept()

    def __store_state(self):
        s = self.settings

        s.beginGroup("Application")
        s.setValue("state", self.saveState())
        s.setValue("geometry", self.saveGeometry())
        s.endGroup()

        s.beginGroup("InstancesView")
        self.instances.store_state(s)
        s.endGroup()

    def __restore_state(self):
        s = self.settings

        s.beginGroup("Application")
        ws = s.value("state")
        if ws:
            self.restoreState(ws)

        wg = s.value("geometry")
        if wg:
            self.restoreGeometry(wg)
        s.endGroup()

        s.beginGroup("InstancesView")
        self.instances.restore_state(s)
        s.endGroup()


if __name__ == '__main__':
    import sys

    try:
        app = QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
