import collections

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QDialog, QApplication, QDialogButtonBox, QFormLayout, QLineEdit, QLabel, \
    QHBoxLayout, QSizePolicy, QComboBox, QWidget, QVBoxLayout

from KdbShape.kdb.Authorization import AuthorizationManager
from KdbShape.kdb.KdbInstance import KdbInstance

AuthWidget = collections.namedtuple("AuthWidget", "code widget")


class UpdatedField:
    SYMBOL = 1
    HOST = 2
    PORT = 3
    AUTH = 4
    INVALIDATE = 5


class InstanceDialog(QDialog):
    ValidHostnameRegex = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"

    def __init__(self, instance: KdbInstance = None, parent=None):
        super(InstanceDialog, self).__init__(parent)
        self.setWindowTitle("Instance Details")

        self.nameEditor = QLineEdit()
        self.nameEditor.setPlaceholderText("Will be shown in the tree view")
        if instance:
            self.nameEditor.setText(instance.name)

        self.symbolEditor = QLineEdit()
        self.symbolEditor.setPlaceholderText("`:host:port[:user:password]")
        self.symbolEditor.textEdited.connect(lambda v: self.__validate_fields(UpdatedField.SYMBOL, v))
        self.symbolEditor.editingFinished.connect(lambda: self.__validate_fields(UpdatedField.INVALIDATE))

        self.hostEditor = QLineEdit()
        self.hostEditor.setValidator(QRegExpValidator(QRegExp(InstanceDialog.ValidHostnameRegex)))
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
            self.authEditor.addItem(provider.title(), userData=AuthWidget(code, w))

        self.authEditor.currentTextChanged.connect(self.__action_change_auth)
        self.__action_change_auth()

        card.setLayout(self.authLayout)

        form_layout.addRow("", card)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)
        buttons.addButton("Test", QDialogButtonBox.ActionRole)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addWidget(buttons)

        self.setLayout(main_layout)

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
                ud = self.get_active_auth()
                ud.widget.decode(':'.join(v[2:]))

        else:
            v = (self.hostEditor.text(), self.portEditor.text(), self.get_active_auth().widget.encode())
            self.symbolEditor.setText("`:" + ":".join(v))

        self.__validate_buttons()

    def __validate_buttons(self):
        pass

    def get_active_auth(self) -> AuthWidget:
        return self.authEditor.itemData(self.authEditor.currentIndex())

    def __action_change_auth(self):
        ud = self.get_active_auth()

        layout = self.authLayout
        for w in (layout.itemAt(i).widget() for i in range(layout.count())):
            w.hide()

        ud.widget.show()


if __name__ == '__main__':
    import sys

    try:
        app = QApplication(sys.argv)
        mainWin = InstanceDialog()
        mainWin.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
