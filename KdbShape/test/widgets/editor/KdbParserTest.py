import unittest

from KdbShape.app.widgets.editor.KdbParser import KdbParser


class KdbParserTest(unittest.TestCase):
    def test_styleTest(self):
        with open('sample1.q', 'r') as sample1:
            data = sample1.read()

        parser = KdbParser()
        res = parser.invalidate(data, 0, len(data))

        print(res)
        self.assertEqual(10, len(res))


if __name__ == '__main__':
    unittest.main()
