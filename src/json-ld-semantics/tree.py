class Root:
    def __str__(self):
        return "RootNode"


class Node:
    def __init__(self, fieldName, data, parent=None, process_traversal=True, process_children=False):
        self.fieldName = fieldName
        self.data = data
        self.foundType = Root if self.fieldName == "$" else type(data)
        self.descriptiveType = None
        self.unique = None
        self.default = None
        self.description = None
        self.example = None
        self.regex = None
        self.parent = parent
        self.traversal = {}
        self.children = []

        self.process(traversal=process_traversal, children=process_children)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__} '{self.fieldName}' with {len(self.children)} children{'s' if len(self.children) != 1 else ''}"

    def path(self) -> str:
        if not self.parent:
            return self.fieldName
        name = f".{self.fieldName}" if self.fieldName != "[*]" else self.fieldName
        return self.parent.path() + name

    def all_paths(self, level=0) -> str:
        ret = "  " * level + self.path() + "\n"
        if self.traversal:
            for key, children in self.traversal.items():
                ret += children.all_paths(level + 1)
        return ret

    def process(self, traversal=True, children=False) -> None:
        if isinstance(self.data, dict):
            for key, children in self.data.items():
                if traversal:
                    self.traversal[key] = NodeDict(key, children, parent=self)
                if children:
                    self.children.append(NodeDict(key, children, parent=self))
        elif isinstance(self.data, list):
            for children in self.data:
                if traversal:
                    self.traversal["[*]"] = NodeList(children, parent=self)
                if children:
                    self.children.append(NodeList(children, parent=self))
        else:
            return


class NodeList(Node):
    def __init__(self, contains, parent=None):
        super().__init__("[*]", contains, parent=parent)


class NodeDict(Node):
    def __init__(self, fieldName, contains, parent):
        super().__init__(fieldName, contains, parent=parent)