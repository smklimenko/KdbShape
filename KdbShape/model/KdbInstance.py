ValidHostnameRegex = r"(?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*" \
                     r"(?:[A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])"


class KdbInstance:
    __slots__ = ("__name", "__host", "__port", "__username", "__password", "__f_symbol", "__m_symbol")

    def __init__(self, name: str, host: str, port: int, username: str = None, password: str = None):
        self.__name = name
        self.__host = host
        self.__port = port

        self.__username = username
        self.__password = password

        v = [self.__host, str(self.__port)]
        if self.__username:
            v.append(self.__username)
        elif self.__password:
            v.append("")

        s = "`:" + ":".join(v)
        if self.__password:
            self.__m_symbol = s + ":*****"
            self.__f_symbol = s + ":" + self.__password
        else:
            self.__f_symbol = self.__m_symbol = s

    @property
    def name(self):
        return self.__name

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    def symbol(self, mask=False):
        return self.__m_symbol if mask else self.__f_symbol

    def __str__(self) -> str:
        return self.name + " (" + self.symbol(True) + ")"

    @staticmethod
    def parse(symbol: str):
        d = KdbInstance.parsedict(symbol)
        if d["host"] and d["port"]:
            return KdbInstance("", str(d["host"]), int(d["port"]), d["username"], d["password"])
        return None

    @staticmethod
    def parsedict(symbol: str):
        name = ("host", "port", "username", "password")
        result = dict.fromkeys(name)

        s = symbol.lstrip("`:").split(":")
        for i in range(min(len(s), 3)):
            result[name[i]] = s[i]

        # Password could have ':' letters
        if len(s) > 3:
            result["password"] = ":".join(s[3:])

        return result
