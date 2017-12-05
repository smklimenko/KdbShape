from KdbShape.kdb.KdbInstance import KdbInstance
from KdbShape.kdb.conn import open_q_connection, close_q_connection


class CommunicationError(Exception):
    pass


class CommunicationManager:
    def __init__(self):
        super().__init__()

    def change_instance(self, uri):
        print("ServerView: sever changed to" + uri)
        # self.serverChanged.emit(uri)

    def test_instance(self, instance: KdbInstance):
        try:
            close_q_connection(open_q_connection(instance))
        except Exception as e:
            raise CommunicationError("An instance testing is not ready: " + str(e))
        return True
