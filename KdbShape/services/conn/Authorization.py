import abc
import sys
import traceback
from typing import Optional

from PyQt5.QtCore import QRegExp, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFormLayout, QLineEdit

from KdbShape.services.conn.ConnectionManager import Credentials


class AuthorizationWidget(QWidget):
    __slots__ = ("__title",)

    credentialsChanged = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.__title = title

    @property
    def title(self):
        return self.__title

    @abc.abstractmethod
    def encode(self) -> Optional[Credentials]:
        raise NotImplementedError()

    @abc.abstractmethod
    def decode(self, credentials: Credentials):
        raise NotImplementedError()

    @abc.abstractmethod
    def validate(self) -> bool:
        raise NotImplementedError()


class AuthorizationProvider:
    @abc.abstractmethod
    def widget(self) -> AuthorizationWidget:
        raise NotImplementedError()

    @abc.abstractmethod
    def resolve(self, credentials: Credentials) -> Credentials:
        raise NotImplementedError()


class AuthorizationManager:
    __providers = {}

    @staticmethod
    def codes():
        return AuthorizationManager.__providers.keys()

    @staticmethod
    def provider(code: str) -> AuthorizationProvider:
        return AuthorizationManager.__providers[code.lower()]

    @staticmethod
    def register(code: str, provider):
        AuthorizationManager.__providers[code.lower()] = provider

    @staticmethod
    def unregister(code: str):
        del AuthorizationManager.__providers[code]

    @staticmethod
    def resolve(instance: KdbInstance, context: AuthorizationContext = None) -> KdbInstance:
        credentials = instance.credentials
        if not credentials and context:
            credentials = context.credentials()

        if not credentials:
            return instance

        if credentials.username not in {"", "basic"}:
            provider = AuthorizationManager.provider(credentials.username)
            if provider:
                credentials = provider.resolve(credentials)
                if credentials:
                    instance = KdbInstance(instance.name, instance.host, instance.port,
                                           credentials.username, credentials.password)
                else:
                    instance = KdbInstance(instance.name, instance.host, instance.port)
        return instance


class InheritAuthorizationProvider(AuthorizationProvider):
    class TheWidget(AuthorizationWidget):
        def __init__(self, parent=None):
            super().__init__("Inherit from the Tree View", parent)

            label = QLabel("Login/Password will be taken from "
                           "the Tree View settings or from global settings if first one is not specified.")
            label.setWordWrap(True)

            layout = QHBoxLayout()
            layout.addWidget(label)
            layout.setContentsMargins(0, 0, 0, 0)

            self.setLayout(layout)

        def validate(self) -> bool:
            return True

        def decode(self, credentials: Credentials):
            pass

        def encode(self) -> Optional[Credentials]:
            return None

    def widget(self, parent=None):
        return InheritAuthorizationProvider.TheWidget(parent)

    def resolve(self, credentials: Credentials) -> Credentials:
        return credentials


class BasicAuthorizationProvider(AuthorizationProvider):
    class TheWidget(AuthorizationWidget):
        def __init__(self, parent):
            super().__init__("Username/Password", parent)

            self.loginEditor = QLineEdit()
            self.loginEditor.setValidator(QRegExpValidator(QRegExp(r"[^:]*")))
            self.loginEditor.setPlaceholderText("Anything without ':' letter or empty")
            self.loginEditor.textEdited.connect(self.__fields_changed)

            self.passwordEditor = QLineEdit()
            self.passwordEditor.setPlaceholderText("Anything or empty")
            self.passwordEditor.setEchoMode(QLineEdit.Password)
            self.passwordEditor.textEdited.connect(self.__fields_changed)

            layout = QFormLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            layout.addRow("Login:", self.loginEditor)
            layout.addRow("Password:", self.passwordEditor)

            self.setLayout(layout)

        def decode(self, credentials: Credentials):
            self.loginEditor.setText(credentials.username if credentials else "")
            self.passwordEditor.setText(credentials.password if credentials else "")

        def encode(self) -> Optional[Credentials]:
            return Credentials(self.loginEditor.text(), self.passwordEditor.text())

        def validate(self) -> bool:
            return True

        def __fields_changed(self):
            try:
                self.credentialsChanged.emit()
            except Exception as e:
                print(e)
                traceback.print_exc(file=sys.stdout)

    def resolve(self, credentials: Credentials) -> Credentials:
        return credentials

    def widget(self, parent=None):
        return BasicAuthorizationProvider.TheWidget(parent)


AuthorizationManager.register("", InheritAuthorizationProvider())
AuthorizationManager.register("basic", BasicAuthorizationProvider())
