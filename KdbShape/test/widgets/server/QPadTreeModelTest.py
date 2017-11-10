import unittest

from KdbShape.widgets.server.QPadTreeModel import QPadTreeModel


class QPadTreeModelTest(unittest.TestCase):
    def test_styleTest(self):
        model = QPadTreeModel('qpad.cfg')


if __name__ == '__main__':
    unittest.main()
