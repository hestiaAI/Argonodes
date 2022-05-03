"""
semantics.py is everything linked to a single file.
"""
from typing import Optional
import json
import re


from .abstract import Protected


REGEX_PATH = re.compile(r"\[\d+\]")


class Root:
    """
    Special type for the root of a Tree.
    """

    def __str__(self):
        return "RootNode"


def make_traversal(node) -> dict:
    void = {}

    def recur(node, void) -> None:
        path = REGEX_PATH.sub("[*]", node.path)
        if path not in void:
            void[path] = {
                "foundType": node.foundType,
                "descriptiveType": node.descriptiveType,
                "unique": node.unique,
                "default": node.default,
                "description": node.description,
                "example": node.example,
                "regex": node.regex,
                "traversal": {},
            }
        if node.children:
            for children in node.children:
                recur(children, void[path]["traversal"])
        else:
            return

    recur(node, void)
    return void


def flatten_traversal(traversal):
    def recur(traversal):
        for k, v in traversal.items():
            yield k
            if v:
                yield from (r for r in recur(v["traversal"]))

    return set(recur(traversal))


class Node:
    """
    A Node is a specific part of the JSON Tree.
    """

    __metaclass__ = Protected

    def __init__(self, data, fieldName, parent=None, process_traversal=False):
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
        self.path = self._set_path()

        self._process(process_traversal=process_traversal)

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
            if attr in ["children", "traversal"]:
                # Skip
                continue
            elif attr in ["data"]:
                rep += f"- {attr}: Length of {len(str(getattr(self, attr)))}\n"
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
        name = f".{self.fieldName}" if not REGEX_PATH.match(self.fieldName) else self.fieldName
        return self.parent.path + name

    def get_paths(self) -> set:
        """
        All paths linked to that Node.
        :return: Set[String], set of avalaible paths.
        """

        def recur(node):
            yield REGEX_PATH.sub("[*]", node.path)
            if node.children:
                for children in node.children:
                    yield from (r for r in recur(children))

        return set(recur(self))

    def get_paths_fancy(self) -> str:
        """
        A printable and formated list of Paths.
        :return: String, fancy paths list.
        """

        def recur(node, align=0):
            yield " " * align + REGEX_PATH.sub("[*]", node.path)
            if node.children:
                for children in node.children:
                    yield from (r for r in recur(children, align=align + 1))

        return "\n".join(sorted(set(r for r in recur(self)), key=lambda x: x.strip()))

    def _process(self, process_traversal) -> None:
        """
        Internal, create the hierarchy for that Node.
        It can either be used for the whole data, or for the structure only.
        :param process_traversal: Boolean, should the Node process its traversal.
        :param process_children: Boolean, should the Node process its children.
        :return: None.
        """
        if isinstance(self.data, dict):
            for key, children in self.data.items():
                self.children.append(
                    NodeDict(children, fieldName=key, parent=self, process_traversal=process_traversal)
                )
        elif isinstance(self.data, list):
            for i, children in enumerate(self.data):
                self.children.append(NodeList(children, i=i, parent=self, process_traversal=process_traversal))
        else:
            return

        if process_traversal:
            self.traversal = make_traversal(self)

            assert flatten_traversal(self.traversal) == self.get_paths()

    def export_traversal(self) -> dict:
        """
        Export the created traversal, if it exists.
        :return: Dict, the traversal.
        """
        if not self.traversal:
            self.traversal = make_traversal(self)

            assert flatten_traversal(self.traversal) == self.get_paths()

        return self.traversal

    def get_attributes(self) -> list:
        """
        List of all attributes available.
        :return: List of all attributes available.
        """
        return list(self.__dict__.keys())

    def get_children_from_path(self, path) -> list:
        regex = re.compile(
            r"^"
            + path.replace("$", r"\$").replace(".", r"\.").replace("[", r"\[").replace("]", r"\]").replace("*", r".*")
            + r"$"
        )

        def recur(path):
            if regex.match(self.path):
                yield self
            if self.children:
                for children in self.children:
                    yield from (r for r in children.get_children_from_path(path))

        return list(recur(path))

    def apply(self, item) -> bool:
        if not self.traversal:
            if not self.traversal:
                self.traversal = make_traversal(self)
        from .filters import Filter  # Local scope
        from .model import Model  # Local scope

        if isinstance(item, Model):
            flat = item.flatten()

            def recur(node):
                path = REGEX_PATH.sub("[*]", node.path)
                info = flat[path]
                node.descriptiveType = info["descriptiveType"]
                node.unique = info["unique"]
                node.default = info["default"]
                node.description = info["description"]
                node.example = info["example"]
                node.regex = info["regex"]
                if node.children:
                    for children in node.children:
                        recur(children)

            recur(self)

            return True
        elif isinstance(item, Filter):
            if item.paths:
                pass  # TODO
            if item.filters:

                def recur(traversal, filtr):
                    attr, op, value = filtr
                    for path, info in traversal.items():
                        if info["traversal"]:
                            recur(info["traversal"], filtr)
                        if hasattr(info, attr) and not op(info[attr], value):
                            traversal.pop(path)

                for filtr in item.filters:
                    recur(self.traversal, filtr)
        else:
            raise ValueError("`item` should be either a Model or a Filter.")


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

    def __init__(self, contains, parent, process_traversal, i=None):
        super().__init__(
            contains,
            fieldName=f"[{i}]" if i is not None else "[*]",
            parent=parent,
            process_traversal=process_traversal,
        )


class NodeDict(Node):
    """
    A NodeDict is a special Node that contains data in a dict.
    """

    def __init__(self, contains, fieldName, parent, process_traversal):
        super().__init__(
            contains,
            fieldName=fieldName,
            parent=parent,
            process_traversal=process_traversal,
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
