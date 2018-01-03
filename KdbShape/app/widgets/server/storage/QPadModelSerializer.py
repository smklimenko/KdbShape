from collections import deque

from PyQt5.QtCore import QModelIndex

from KdbShape.app.widgets.server.InstancesTreeModel import InstancesTreeModel


class QPadModelSerializer:
    def __init__(self, file: str):
        self.file = file

    def load_model(self, model: InstancesTreeModel):
        with open(self.file, encoding="utf-8") as f:
            data = f.read().splitlines()

        for line in data:
            tokens = line.strip()[1:].split('`')

            parent_index = QModelIndex()
            for name in tokens[1:-1]:
                item_index = model.findByName(parent_index, name)
                if item_index.isValid():
                    parent_index = item_index
                else:
                    parent_index = model.insertFolder(name, -1, parent_index)
            model.insertInstance(tokens[-1], '`' + tokens[0], -1, parent_index)

    def save_model(self, model: InstancesTreeModel):
        instances = []

        to_crawl = deque([model.rootItem])
        while to_crawl:
            current = to_crawl.popleft()
            if current.isInstance():
                instances.append(current)
            else:
                to_crawl.extend(current.children())

        with open(self.file, mode="w", encoding="utf-8") as f:
            for n in instances:
                f.write(n.getUri())
                f.write(n.getPath())
                f.write('\n')
