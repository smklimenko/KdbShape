import json

from KdbShape.widgets.server.InstancesTreeModel import InstancesTreeModel


class JSONModelSerializer:
    def __init__(self, file: str):
        self.file = file

    def load_model(self, model: InstancesTreeModel):
        pass

    def save_model(self, model: InstancesTreeModel):
        d = {}
        self.__save_model_node(model.rootItem, d)
        print(json.dumps(d[''], indent=2))

    @staticmethod
    def __save_model_node(item, d):
        if item.isInstance():
            d[item.getName()] = item.getUri()
        else:
            cd = {}
            for c in item.children():
                JSONModelSerializer.__save_model_node(c, cd)
            d[item.getName()] = cd
