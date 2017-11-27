import abc
from typing import Optional

from PyQt5.QtCore import QRegExp, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFormLayout, QLineEdit

from KdbShape.kdb.KdbInstance import KdbInstance


class AuthorizationWidget(QWidget):
    credentialsChanged = pyqtSignal('QString')

    def __init__(self, parent=None):
        super().__init__(parent)

    @abc.abstractmethod
    def decode(self, credentials: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def encode(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def validate(self) -> bool:
        raise NotImplementedError()


class AuthorizationProvider:
    def __init__(self, title):
        super().__init__()
        self.__title = title

    def title(self):
        return self.__title

    @abc.abstractmethod
    def create_widget(self) -> AuthorizationWidget:
        raise NotImplementedError()

    @abc.abstractmethod
    def resolve(self, instance: KdbInstance) -> Optional[str]:
        raise NotImplementedError()


class AuthorizationManager:
    __providers = {}

    @staticmethod
    def codes():
        return AuthorizationManager.__providers.keys()

    @staticmethod
    def provider(code) -> AuthorizationProvider:
        v = AuthorizationManager.__providers[code.lower()]
        return v()

    @staticmethod
    def register(code, provider):
        AuthorizationManager.__providers[code.lower()] = provider

    @staticmethod
    def unregister(code):
        del AuthorizationManager.__providers[code]


class NoAuthorizationProvider(AuthorizationProvider):
    class TheWidget(AuthorizationWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            label = QLabel("Login/Password will be taken from "
                           "the Tree View settings or from global settings if first one is not specified.")
            label.setWordWrap(True)

            layout = QHBoxLayout()
            layout.addWidget(label)
            layout.setContentsMargins(0, 0, 0, 0)

            self.setLayout(layout)

        def validate(self) -> bool:
            return True

        def encode(self) -> str:
            return ""

        def decode(self, credentials: str):
            pass

    def __init__(self):
        super().__init__("Inherit from the Tree View")

    def create_widget(self, parent=None):
        return NoAuthorizationProvider.TheWidget(parent)

    def resolve(self, instance: KdbInstance) -> Optional[str]:
        return None


class BasicAuthorizationProvider(AuthorizationProvider):
    class TheWidget(AuthorizationWidget):
        def __init__(self, parent):
            super().__init__(parent)

            self.loginEditor = QLineEdit()
            self.loginEditor.setValidator(QRegExpValidator(QRegExp(r"[^:]*")))
            self.loginEditor.setPlaceholderText("Anything without ':' letter or empty")
            self.loginEditor.textEdited.connect(self.__fields_changed)

            self.passwordEditor = QLineEdit()
            self.passwordEditor.setPlaceholderText("Anything or empty")
            self.passwordEditor.textEdited.connect(self.__fields_changed)

            w = QWidget()

            layout = QFormLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            layout.addRow("Login:", self.loginEditor)
            layout.addRow("Password:", self.passwordEditor)

            self.setLayout(layout)

        def encode(self) -> str:
            if self.passwordEditor.text():
                return self.loginEditor.text() + ":" + self.passwordEditor.text()
            return self.loginEditor.text()

        def decode(self, credentials: str):
            try:
                i = credentials.index(":")
                self.loginEditor.setText(credentials[:i])
                self.passwordEditor.setText(credentials[i+1:])
            except ValueError:
                self.loginEditor.setText(credentials)
                self.passwordEditor.setText("")

        def validate(self) -> bool:
            return True

        def __fields_changed(self):
            self.credentialsChanged.emit(self.encode())

    def __init__(self):
        super().__init__("Username/Password")

    def resolve(self, instance: KdbInstance):
        return instance.credentials()

    def create_widget(self, parent=None):
        return BasicAuthorizationProvider.TheWidget(parent)


AuthorizationManager.register("", NoAuthorizationProvider)
AuthorizationManager.register("basic", BasicAuthorizationProvider)
