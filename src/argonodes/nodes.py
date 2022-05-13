"""
semantics.py is everything linked to a single file.
"""
from __future__ import annotations


from typing import Union


from .applies import make_traversal
from .helpers import REGEX_PATH, REGEX_SEARCH


MAX_DATA = 128
PROTECTED_ATTRS = ["fieldName", "data", "foundType", "parent", "children", "path"]


class Root:
    """
    Special type for the root of a Tree.
    """

    def __str__(self):
        return "RootNode"


class Node:
    """
    A Node is a specific part of the JSON Tree.

    :param data: 1
    :type data: test
    :param fieldName: 2
    :param parent: 3
    :param process_traversal: 4
    """

    def __init__(self, data, fieldName, parent=None, process_traversal=False) -> None:
        self.fieldName = fieldName
        self.foundType = Root if self.fieldName == "$" else type(data)
        self.descriptiveType = None
        self.unique = None
        self.default = None
        self.description = None
        self.choices = None  # If None, means there is no preset values.
        self.regex = None
        self.parent = parent
        self.traversal = {}
        self.children = []
        self.path = self._set_path()

        self._process(data, process_traversal=process_traversal)

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
            elif attr in ["data"] and getattr(self, attr):
                rep += f"- {attr}: \"{str(getattr(self, attr))[:MAX_DATA]}{'...' if len(str(getattr(self, attr))) > MAX_DATA else ''}\" (length of {len(str(getattr(self, attr)))})\n"
            elif attr in ["foundType"]:
                rep += f"- {attr}: {getattr(self, attr).__name__}\n"
            elif attr in ["parent"]:
                rep += f"- {attr}: {getattr(self, attr).fieldName if getattr(self, attr) else None}\n"
            else:
                rep += f"- {attr}: {getattr(self, attr)}\n"
        return rep

    def __setattr__(self, key, value):
        if key in PROTECTED_ATTRS and hasattr(self, key):
            raise AttributeError(f"Cannot modify `{key}`.")
        else:
            return super().__setattr__(key, value)

    def __delattr__(self, item):
        if item in PROTECTED_ATTRS:
            raise AttributeError(f"Cannot delete `{item}`.")
        else:
            return super().__delattr__(item)

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
        A printable and formatted list of Paths.

        :return: String, fancy paths list.
        """

        def recur(node, align=0):
            yield " " * align + REGEX_PATH.sub("[*]", node.path)
            if node.children:
                for children in node.children:
                    yield from (r for r in recur(children, align=align + 1))

        return "\n".join(sorted(set(r for r in recur(self)), key=lambda x: x.strip()))

    def _process(self, data, process_traversal) -> None:
        """
        Internal, create the hierarchy for that Node.

        It can either be used for the whole data, or for the structure only.

        :param process_traversal: Boolean, should the Node process its traversal.
        :return: None.
        """
        if isinstance(data, dict):
            self.data = None
            for key, children in data.items():
                self.children.append(
                    NodeDict(children, fieldName=key, parent=self, process_traversal=process_traversal)
                )
        elif isinstance(data, list):
            self.data = None
            for i, children in enumerate(data):
                self.children.append(NodeList(children, i=i, parent=self, process_traversal=process_traversal))
        else:
            self.data = data

        if process_traversal:
            self.apply(make_traversal)

    def export_traversal(self) -> dict:
        """
        Export the created traversal, if it exists.

        :return: Dict, the traversal.
        """
        if not self.traversal:
            self.apply(make_traversal)

        return self.traversal

    def get_attributes(self) -> list:
        """
        List of all attributes available.

        :return: List of all attributes available.
        """
        return list(self.__dict__.keys())

    def get_children_from_path(self, path) -> list:
        def recur(target):
            if REGEX_SEARCH(target).match(self.path):
                yield self
            if self.children:
                for children in self.children:
                    yield from (r for r in children.get_children_from_path(target))

        return list(recur(path))

    def apply(self, fun, rec=True, *args, **kwargs) -> Union[Node, object]:
        """
        Takes a function that will be applied to the node and/or children, and potential arguments.

        :param fun: A Node function
        :param rec: Should the function be applied recursively (all children) or not.
        :return: Self if the function does not return anything, else whatever the function returns.
        """
        rtr = fun(self, rec, *args, **kwargs)
        if rtr:
            return rtr
        else:
            return self


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
