import unittest

from KdbShape.model.KdbInstance import KdbInstance


class KdbInstanceTest(unittest.TestCase):
    def test_symbol(self):
        self.assertEqual("`:host:1212", KdbInstance("name", "host", 1212).symbol(False))
        self.assertEqual("`:host:1212", KdbInstance("name", "host", 1212).symbol(True))

        self.assertEqual("`:host:1212:asd", KdbInstance("name", "host", 1212, "asd").symbol(False))
        self.assertEqual("`:host:1212:asd", KdbInstance("name", "host", 1212, "asd").symbol(True))

        self.assertEqual("`:host:1212:asd:qwe", KdbInstance("name", "host", 1212, "asd", "qwe").symbol(False))
        self.assertEqual("`:host:1212:asd:*****", KdbInstance("name", "host", 1212, "asd", "qwe").symbol(True))

        self.assertEqual("`:host:1212::qwe", KdbInstance("name", "host", 1212, password="qwe").symbol(False))
        self.assertEqual("`:host:1212::*****", KdbInstance("name", "host", 1212, password="qwe").symbol(True))

    def test_parse(self):
        self.assertEqual("`:host:1212", KdbInstance.parse("`:host:1212").symbol())
        self.assertEqual("`:host:1212:asd", KdbInstance.parse("`:host:1212:asd").symbol())
        self.assertEqual("`:host:1212:asd:qwe", KdbInstance.parse("`:host:1212:asd:qwe").symbol())
        self.assertEqual("`:host:1212::qwe", KdbInstance.parse("`:host:1212::qwe").symbol())
        self.assertEqual("`:host:1212:asd:qwe:zxcv", KdbInstance.parse("`:host:1212:asd:qwe:zxcv").symbol())
        self.assertEqual("`:host:1212:asd:qwe:zxcv", KdbInstance.parse(":host:1212:asd:qwe:zxcv").symbol())
        self.assertEqual("`:host:1212:asd:qwe:zxcv", KdbInstance.parse("host:1212:asd:qwe:zxcv").symbol())
        self.assertIsNone(KdbInstance.parse("host"))

    def test_parsedict(self):
        d = KdbInstance.parsedict("host")
        self.assertEqual("host", d["host"])
        self.assertIsNone(d["port"])
        self.assertIsNone(d["username"])
        self.assertIsNone(d["password"])

        d = KdbInstance.parsedict("`:host")
        self.assertEqual("host", d["host"])

        d = KdbInstance.parsedict("`:host:12214234::")
        self.assertEqual("host", d["host"])
        self.assertEqual("12214234", d["port"])
        self.assertEqual("", d["username"])
        self.assertEqual("", d["password"])


if __name__ == '__main__':
    unittest.main()
