"""
semantics.py is everything linked to a single file.
"""
from typing import Optional
import json


class Root:
    """
    Special type for the root of a Tree.
    """

    def __str__(self):
        return "RootNode"


class Node:
    """
    A Node is a specific part of the JSON Tree.
    """

    def __init__(self, data, fieldName, parent=None, process_traversal=True, process_children=True):
        self.fieldName = fieldName
        self.data = data
        self.foundType = Root if self.fieldName == "$" else type(data)
        # self.descriptiveType = None
        # self.unique = None
        # self.default = None
        # self.description = None
        # self.example = None
        # self.regex = None
        self.parent = parent
        self.traversal = {}
        self.children = []
        self.path = self._set_path()

        self._process(traversal=process_traversal, children=process_children)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        rep = f"{type(self).__name__} '{self.fieldName}'"
        if self.children:
            rep += f" with {len(self.children)} children{'s' if len(self.children) != 1 else ''}"
        if self.children and self.traversal:
            rep += " and"
        if self.traversal:
            rep += f" with {len(self.get_paths())} path{'s' if len(self.get_paths()) != 1 else ''}"
        rep += "\n"
        for attr in self.get_attributes():
            if attr in ["data", "children"]:
                rep += f"- {attr}: Length of {len(getattr(self, attr))}\n"
            elif attr in ["traversal"]:
                rep += f"- {attr}: {len(self.get_paths())} path{'s' if len(self.get_paths()) != 1 else ''}\n"
            elif attr in ["foundType"]:
                rep += f"- {attr}: {getattr(self, attr).__name__}\n"
            elif attr in ["parent"]:
                rep += f"- {attr}: {getattr(self, attr).fieldName if getattr(self, attr) else None}\n"
            else:
                rep += f"- {attr}: {getattr(self, attr)}\n"
        return rep

    def _set_path(self) -> str:
        """
        Internal, set the path for that Node.
        :return: String, path for that Node.
        """
        if not self.parent:
            return self.fieldName
        name = f".{self.fieldName}" if self.fieldName != "[*]" else self.fieldName
        return self.parent.path + name

    def get_paths(self) -> set:
        """
        All paths linked to that Node.
        :return: Set[String], set of avalaible paths.
        """

        def recur(inner):
            yield inner.path
            if inner.traversal:
                for key, children in inner.traversal.items():
                    yield from (path for path in recur(children))

        return set(recur(self))

    def get_paths_fancy(self, level=0) -> str:
        """
        A printable and formated list of Paths.
        :param level: Used for recursion.
        :return: String, fancy paths list.
        """
        ret = "  " * level + self.path + "\n"
        if self.traversal:
            for key, children in self.traversal.items():
                ret += children.get_paths_fancy(level + 1)
        return ret

    def _process(self, traversal, children) -> None:
        """
        Internal, create the hierarchy for that Node.
        It can either be used for the whole data, or for the structure only.
        :param traversal: Boolean, should the Node process its traversal.
        :param children: Boolean, should the Node process its children.
        :return: None.
        """
        if isinstance(self.data, dict):
            for key, children in self.data.items():
                if traversal:
                    self.traversal[key] = NodeDict(
                        children, fieldName=key, parent=self, process_traversal=traversal, process_children=children
                    )
                if children:
                    self.children.append(
                        NodeDict(
                            children, fieldName=key, parent=self, process_traversal=traversal, process_children=children
                        )
                    )
        elif isinstance(self.data, list):
            for i, children in enumerate(self.data):
                if traversal:
                    self.traversal["[*]"] = NodeList(
                        children, parent=self, process_traversal=traversal, process_children=children
                    )
                if children:
                    self.children.append(
                        NodeList(children, i=i, parent=self, process_traversal=traversal, process_children=children)
                    )
        else:
            return

    def export_traversal(self, with_root=True) -> dict:
        """
        Export the created traversal, if it exists.
        :param with_root: If True, add the root at the begining.
        :return: Dict, the traversal.
        """

        def treeify(inner_traversal, root="$"):
            data = {}
            for key, node in inner_traversal.items():
                data.update(
                    {
                        key: {
                            "path": f"{root}{'.' if isinstance(node, NodeDict) else ''}{key}",
                            "foundType": node.foundType,
                            "descriptiveType": None,
                            "unique": None,
                            "default": None,
                            "description": None,
                            "example": None,
                            "regex": None,
                            "traversal": treeify(
                                node.traversal, root=f"{root}{'.' if isinstance(node, NodeDict) else ''}{key}"
                            ),
                        }
                    }
                )

            return data

        if with_root:
            return {
                "$": {
                    "path": "$",
                    "foundType": Root,
                    "descriptiveType": None,
                    "unique": None,
                    "default": None,
                    "description": None,
                    "example": None,
                    "regex": None,
                    "traversal": treeify(self.traversal),
                }
            }
        else:
            return treeify(self.traversal)

    def get_attributes(self) -> list:
        """
        List of all attributes available.
        :return: List of all attributes available.
        """
        return list(self.__dict__.keys())

    def get_children_from_path(self, path) -> Optional:
        if not self.children:
            return None
        if self.path not in path:
            return None
        if self.path == path:
            return self
        else:
            for children in self.children:
                if children.path in path:
                    return children.get_children_from_path(path)


class Tree(Node):
    """
    A Tree is a special Node with `$` as field name.
    """

    def __init__(self, data):
        super().__init__(data, fieldName="$")


class NodeList(Node):
    """
    A NodeList is a special Node that contains data in a list.
    """

    def __init__(self, contains, parent, process_traversal, process_children, i=None):
        super().__init__(
            contains,
            fieldName=f"[{i}]" if i is not None else "[*]",
            parent=parent,
            process_traversal=process_traversal,
            process_children=process_children,
        )


class NodeDict(Node):
    """
    A NodeDict is a special Node that contains data in a dict.
    """

    def __init__(self, contains, fieldName, parent, process_traversal, process_children):
        super().__init__(
            contains,
            fieldName=fieldName,
            parent=parent,
            process_traversal=process_traversal,
            process_children=process_children,
        )


def get_extended_traversal(tree_traversal, raw=False):
    def recur(inner_tree_traversal):
        tmp = []

        for key, node in inner_tree_traversal.items():
            if isinstance(node, NodeList):
                tmp.append(node.get_frame(contains="[" + recur(node.traversal) + "]"))
            else:
                if node.traversal:
                    tmp.append(node.get_frame(contains="[" + recur(node.traversal) + "]"))
                else:
                    tmp.append(node.get_frame())

        tmp = ",".join(tmp).replace("\\", "")
        return tmp

    if raw:
        return recur(tree_traversal)
    else:
        return json.loads(recur(tree_traversal))
