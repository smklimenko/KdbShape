import collections

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QDialog, QApplication, QDialogButtonBox, QFormLayout, QLineEdit, QLabel, \
    QHBoxLayout, QSizePolicy, QComboBox, QWidget, QVBoxLayout, QMessageBox

from KdbShape.kdb.Authorization import AuthorizationManager
from KdbShape.kdb.CommunicationManager import CommunicationManager, CommunicationError
from KdbShape.kdb.KdbInstance import *
from KdbShape.plugins import PlyginsManager

AuthItem = collections.namedtuple("AuthWidget", "code widget")


class UpdatedField:
    SYMBOL = 1
    HOST = 2
    PORT = 3
    AUTH = 4
    INVALIDATE = 5


class InstanceDialog(QDialog):
    def __init__(self, connection_manager: CommunicationManager, instance: KdbInstance = None, parent=None):
        super(InstanceDialog, self).__init__(parent)
        self.setWindowTitle("Instance Details")

        self.connectionManager = connection_manager

        self.nameEditor = QLineEdit()
        self.nameEditor.setPlaceholderText("Will be shown in the tree view")
        if instance:
            self.nameEditor.setText(instance.name)

        self.symbolEditor = QLineEdit()
        self.symbolEditor.setPlaceholderText("`:host:port[:user:password]")
        self.symbolEditor.textEdited.connect(lambda v: self.__validate_fields(UpdatedField.SYMBOL, v))
        self.symbolEditor.editingFinished.connect(lambda: self.__validate_fields(UpdatedField.INVALIDATE))

        self.hostEditor = QLineEdit()
        self.hostEditor.setValidator(QRegExpValidator(QRegExp(ValidHostnameRegex)))
        self.hostEditor.textEdited.connect(lambda v: self.__validate_fields(UpdatedField.HOST, v))
        self.hostEditor.setPlaceholderText("Hostname or IP or empty")

        self.portEditor = QLineEdit()
        self.portEditor.setValidator(QIntValidator(0, 65535))
        self.portEditor.setPlaceholderText("Port number")
        self.portEditor.textEdited.connect(lambda v: self.__validate_fields(UpdatedField.PORT, v))

        form_layout = QFormLayout()
        form_layout.addRow("Name:", self.nameEditor)
        form_layout.addRow("Symbol:", self.symbolEditor)

        server_layout = QHBoxLayout()
        sp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sp.setHorizontalStretch(2)
        self.hostEditor.setSizePolicy(sp)
        server_layout.addWidget(self.hostEditor)

        server_layout.addWidget(QLabel(":"))

        sp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sp.setHorizontalStretch(1)
        self.portEditor.setSizePolicy(sp)
        server_layout.addWidget(self.portEditor)

        form_layout.addRow("Address:", server_layout)

        self.authEditor = QComboBox()
        form_layout.addRow("Authentication:", self.authEditor)

        card = QWidget()
        self.authLayout = QVBoxLayout()
        self.authLayout.setAlignment(Qt.AlignTop)
        self.authLayout.setContentsMargins(0, 0, 0, 0)

        for code in AuthorizationManager.codes():
            provider = AuthorizationManager.provider(code)

            w = provider.create_widget()
            w.credentialsChanged.connect(lambda v: self.__validate_fields(UpdatedField.AUTH, v))
            w.hide()

            self.authLayout.addWidget(w)
            self.authEditor.addItem(provider.title(), userData=AuthItem(code, w))

        self.authEditor.currentTextChanged.connect(self.__action_change_auth)

        card.setLayout(self.authLayout)

        form_layout.addRow("", card)

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)

        self.textButton = self.buttons.addButton("Test", QDialogButtonBox.ActionRole)
        self.textButton.pressed.connect(self.__test_current)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.buttons)

        self.setLayout(main_layout)

        self.__validate_fields(UpdatedField.INVALIDATE, None)

    def create_instance(self):
        auth = self.__active_auth()

        name = self.nameEditor.text().strip()
        host = self.hostEditor.text().strip()
        port = int(self.portEditor.text().strip())
        return KdbInstance(name, host, port, auth.code, auth.widget.encode())

    def __test_current(self):
        inst = self.create_instance()

        msg = QMessageBox()
        msg.setWindowTitle("An Instance Testing Result")
        msg.setStandardButtons(QMessageBox.Ok)

        try:
            self.connectionManager.test_instance(inst)
            msg.setText("Connected and disconnected successfully")
            msg.setIcon(QMessageBox.Information)
        except CommunicationError as err:
            msg.setText(str(err))
            msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    def __validate_fields(self, source: int, v: str = None):
        if source == UpdatedField.SYMBOL:
            while len(v) > 0 and v[0] in "`:":
                v = v[1:]
            v = v.split(":")

            cnt = len(v)
            if cnt > 0:
                self.hostEditor.setText(v[0])
            if cnt > 1:
                self.portEditor.setText(v[1])
            if cnt > 2:
                ud = self.__active_auth()
                ud.widget.decode(':'.join(v[2:]))

        else:
            v = (self.hostEditor.text(), self.portEditor.text(), self.__active_auth().widget.encode())
            length = sum(len(i) for i in v)
            if length:
                self.symbolEditor.setText("`:" + ":".join(v).strip(":"))
            else:
                self.symbolEditor.setText("")
        self.__validate_buttons()

    def __validate_buttons(self):
        res = True
        # For test only symbol is required
        res = res and len(self.hostEditor.text().strip())
        res = res and len(self.portEditor.text().strip())
        res = res and self.__active_auth().widget.validate()
        self.textButton.setEnabled(res)

        # But for creation - name as well
        res = res and len(self.nameEditor.text().strip())
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(res)

    def __active_auth(self) -> AuthItem:
        return self.authEditor.itemData(self.authEditor.currentIndex())

    def __action_change_auth(self):
        ud = self.__active_auth()

        layout = self.authLayout
        for w in (layout.itemAt(i).widget() for i in range(layout.count())):
            w.hide()

        ud.widget.show()


if __name__ == '__main__':
    import sys


    def dlg_f(result):
        if result == QDialog.Accepted:
            print(mainWin.create_instance())


    try:
        PlyginsManager.initialize()

        m = CommunicationManager()

        app = QApplication(sys.argv)
        mainWin = InstanceDialog(m)
        mainWin.show()

        mainWin.finished.connect(dlg_f)

        sys.exit(app.exec_())
    except Exception as e:
        print(e)
