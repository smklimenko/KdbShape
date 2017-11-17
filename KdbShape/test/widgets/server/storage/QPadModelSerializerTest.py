import unittest

from KdbShape.widgets.server.InstancesTreeModel import InstancesTreeModel
from KdbShape.widgets.server.storage.QPadModelSerializer import QPadModelSerializer


class QPadModelSerializerTest(unittest.TestCase):
    def test_serializer(self):
        s = QPadModelSerializer('qpad.cfg')

        m = InstancesTreeModel()
        s.load_model(m)

        print(m.rootItem)


if __name__ == '__main__':
    unittest.main()
