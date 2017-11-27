class KdbInstance:
    __slots__ = ("name", "symbol", "authorization")

    def __init__(self, name: str, symbol: str, authorization: str = None):
        super(KdbInstance).__init__()

        self.name = name
        self.symbol = symbol
        self.authorization = authorization

    def credentials(self):
        v = self.symbol.split(":")
        if len(v) < 3:
            return None
        return ":".join(v[2:])
