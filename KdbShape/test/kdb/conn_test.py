import unittest

from KdbShape.kdb.conn import open_q_connection, close_q_connection


class KdbParserTest(unittest.TestCase):
    def test_connetion(self):
        q = open_q_connection("localhost", 20000)
        print(q('.z.t'))
        close_q_connection(q)


if __name__ == '__main__':
    unittest.main()
