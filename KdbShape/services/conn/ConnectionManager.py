from qpython import qconnection

from KdbShape.model.KdbInstance import KdbInstance, Credentials
from KdbShape.services.conn.Authorization import AuthorizationManager


# print(q)
# print('IPC version: %s. Is connected: %s' % (q.protocol_version, q.is_connected()))
#
# # simple query execution via: QConnection.__call__
# data = q('{`int$ til x}', 10)
# print('type: %s, numpy.dtype: %s, meta.qtype: %s, data: %s ' % (type(data), data.dtype, data.meta.qtype, data))
#
# # simple query execution via: QConnection.sync
# data = q.sync('{`long$ til x}', 10)
# print('type: %s, numpy.dtype: %s, meta.qtype: %s, data: %s ' % (type(data), data.dtype, data.meta.qtype, data))
#
# # low-level query and read
# q.query(qconnection.MessageType.SYNC, '{`short$ til x}', 10)  # sends a SYNC query
# msg = q.receive(data_only=False, raw=False)  # retrieve entire message
# print('type: %s, message type: %s, data size: %s, is_compressed: %s ' % (
#     type(msg), msg.type, msg.size, msg.is_compressed))
# data = msg.data
# print('type: %s, numpy.dtype: %s, meta.qtype: %s, data: %s ' % (type(data), data.dtype, data.meta.qtype, data))
# # close connection
# q.close()

class CommunicationError(Exception):
    pass


class Address:
    __slots__ = ("__host", "__port")

    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    def __str__(self) -> str:
        return self.__host + ":" + str(self.__port)


class Credentials:
    __slots__ = ("__username", "__password")

    def __init__(self, username: str = None, password: str = None):
        self.__username = username
        self.__password = password

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @staticmethod
    def create(username: str = None, password: str = None):
        if not username and not password:
            return None
        return Credentials(username, password)


class ConnectionManager:
    def test(self, instance: KdbInstance, default: Credentials = None):
        try:


            credentials = AuthorizationManager.resolve(instance, context)

            return self.__open_connection(instance, credentials)
        except Exception as e:
            raise CommunicationError("An instance testing is not ready: " + str(e))
        return True

    def connect(self, instance: KdbInstance, default_credentials: Credentials = None):
        pass

    @staticmethod
    def __open_connection(address: Address, credentials: Credentials):
        if credentials:
            q = qconnection.QConnection(address.host, address.port,
                                        credentials.username, credentials.password,
                                        encoding="utf-8")
        else:
            q = qconnection.QConnection(address.host, address.port, encoding="utf-8")
        q.open()
        return q
