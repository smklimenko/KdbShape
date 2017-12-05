import collections

ValidHostnameRegex = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"

Credentials = collections.namedtuple("Credentials", "username password")


class KdbInstance:
    __slots__ = ("name", "host", "port", "auth", "credentials")

    def __init__(self, name: str, host: str, port: int, auth: str = None, creds: Credentials = None):
        self.name = name
        self.host = host
        self.port = port

        self.auth = auth
        self.credentials = creds

    def symbol(self):
        r = "`:" + self.host + ":" + str(self.port)
        if self.auth and self.credentials:
            r += self.credentials
        return r

    def __str__(self) -> str:
        return self.name + " (" + self.symbol() + ")"
