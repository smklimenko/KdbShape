# import kdbshape.kdb.conn


class ConnectionMaster:
    _connections = {}

    @staticmethod
    def _normalize_target(target):
        return target

    def connect(self, target):
        normalize_target = self._normalize_target(target)
        pass

    def disconnect(self, target):
        pass

    def _open_connection(self):
        pass
