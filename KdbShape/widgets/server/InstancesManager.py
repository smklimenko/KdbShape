import os

import appdirs

from KdbShape import APPLICATION_NAME
from KdbShape.widgets.server import InstancesTreeModel
from KdbShape.widgets.server.InstancesTreeWidget import InstancesDescriptor
from KdbShape.widgets.server.storage.QPadModelSerializer import QPadModelSerializer


class InstancesManager:
    serializers = {"qp": QPadModelSerializer}

    @staticmethod
    def get_descriptors():
        res = []
        try:
            p = appdirs.user_data_dir(APPLICATION_NAME + "/insts", appauthor=False, roaming=True)
            # files = {name for name in os.listdir(p) if name.lower().endswith(".qp")}

            files = os.listdir(p)
            for f in files:
                name, ext = os.path.splitext(f)
                if ext[0] == '.':
                    ext = ext[1:].lower()

                f = os.path.join(p, f)
                ser = InstancesManager.serializers[ext](f)
                if ser:
                    res.append(InstancesDescriptor(name, ser))
        finally:
            pass
        # except FileNotFoundError as e:
        #     pass

        return res

    def load_instances(self, model: InstancesTreeModel):
        pass

    def store_instances(self, model: InstancesTreeModel, file_format):
        pass
