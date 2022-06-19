"""
Nodes are the building block of the whole pipeline to augment data with semantics.

With Nodes, data can be passed in JSON, which can be explored, described, and tagged, and the nodes can then be used to build data models.

Basic usage: ``tree = Tree(json_data)``
"""
from __future__ import annotations


from typing import Union
import os
import uuid


from .appliers import make_traversal
from .helpers import REGEX_PATH, REGEX_SEARCH


MAX_DATA = 128
PROTECTED_ATTRS = ["fieldName", "filename", "data", "foundType", "parent", "children", "path"]


class Root:
    """
    Special type for the root of a Tree.
    """

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "RootNode"


class NA:
    """
    Special type for Non-Applicable.
    """

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "N/A"


class Node:
    """
    A Node is a specific part of the JSON Tree.

    :param data: Whichever raw data the Node should contains.
    :type data: Any
    :param fieldName: The field name for that Node in the raw JSON data.
    :type fieldName: String
    :param filename: Facultative, what file is the data from.
    :type filename: String, default None.
    :param parent: Facultative, parent for that Node.
    :type parent: Node, default None.
    :param process_traversal: Facultative, whether a traversal should be processed already or not.
    :type process_traversal: bool, default False.
    """

    def __init__(self, data, fieldName, filename=None, parent=None, process_traversal=False) -> None:
        self.fieldName = fieldName
        self.filename = filename
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
        self._path = self._set_path()
        self.path = f"{self.filename}:{self._path}" if self.filename else self._path

        self._process(data, process_traversal=process_traversal, filename=filename)

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
            if attr in ["children", "traversal", "_path"]:
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

        :return: Path for that Node.
        :rtype: str
        """
        if not self.parent:
            return self.fieldName
        name = f".{self.fieldName}" if not REGEX_PATH.match(self.fieldName) else self.fieldName
        return self.parent._path + name

    def get_paths(self) -> set:
        """
        All paths linked to that Node.

        :return: Set of avalaible paths.
        :rtype: set[str]
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

        :return: Fancy paths list.
        :rtype: str
        """

        def recur(node, align=0):
            yield " " * align + REGEX_PATH.sub("[*]", node.path)
            if node.children:
                for children in node.children:
                    yield from (r for r in recur(children, align=align + 1))

        return "\n".join(sorted(set(r for r in recur(self)), key=lambda x: x.strip()))

    def _process(self, data, process_traversal, filename=None) -> None:
        """
        Internal, create the hierarchy for that Node.

        It can either be used for the whole data, or for the structure only.

        :param process_traversal: Should the Node process its traversal.
        :type process_traversal: bool
        """
        if isinstance(data, dict):
            self.data = None
            for key, children in data.items():
                self.children.append(
                    NodeDict(
                        children, fieldName=key, filename=filename, parent=self, process_traversal=process_traversal
                    )
                )
        elif isinstance(data, list):
            self.data = None
            for i, children in enumerate(data):
                self.children.append(
                    NodeList(children, i=i, filename=filename, parent=self, process_traversal=process_traversal)
                )
        else:
            self.data = data

        if process_traversal:
            self.apply(make_traversal)

    def export_traversal(self) -> dict:
        """
        Export the created traversal.

        If the traversal does not exist, it is created.

        :return: The returned traversal.
        :rtype: dict
        """
        self.apply(make_traversal)

        return self.traversal

    def get_attributes(self) -> list:
        """
        List of all attributes available.

        :return: List of all attributes available.
        :rtype: list
        """
        return list(self.__dict__.keys())

    def get_children_from_path(self, paths) -> list:
        """
        Get all children for a given path.

        The path can either be a specific path, or use wildcards.

        :param paths: A single JSONPath or a list of JSONPaths.
        :rtype paths: list[str] or [str]
        :return: The list of all children for the paths.
        :rtype: list[Node]
        """
        if not isinstance(paths, list):
            paths = [paths]

        if self.filename:
            for i, path in enumerate(paths):
                if ":" not in path:
                    paths[i] = f"{self.filename}:{path}"

        def recur(targets):
            for target in targets:
                if REGEX_SEARCH(target).match(self.path):
                    yield self
                if self.children:
                    for children in self.children:
                        yield from (r for r in children.get_children_from_path(targets))

        return list(recur(paths))

    def apply(self, fun, rec=True, *args, **kwargs) -> Union[Node, object]:
        """
        Takes a function that will be applied to the node and/or children, and potential arguments.

        :param fun: A Node function
        :type fun: A function taking into parameters at least the `node` and the `rec` parameters.
        :param rec: Should the function be applied recursively (all children) or not.
        :type rec: bool, default True.
        :return: Self if the function does not return anything, else whatever the function returns.
        :rtype: Node or None.
        """
        rtr = fun(self, rec, *args, **kwargs)
        if rtr:
            return rtr
        else:
            return self

    def delete(self, rec=False, remove=False):
        if rec and self.children:
            for children in self.children:
                children.delete(rec, remove)

        if remove:
            self.parent.children.pop(self)
        else:
            blank_node = Node(None, fieldName=uuid.uuid4(), parent=self.parent)
            blank_node.children += self.children
            self.parent.children.append(blank_node)
            self.parent.children.pop(self)


class Tree(Node):
    """
    A Tree is a special Node with `$` as field name.
    """

    def __init__(self, data, filename=None):
        super().__init__(data, fieldName="$", filename=filename)
        self.unique = NA
        self.default = NA
        self.choices = NA
        self.regex = NA

    def delete(self, rec=False, remove=False):
        raise AssertionError("Cannot delete Root node.")


class NodeList(Node):
    """
    A NodeList is a special Node that contains data in a list.
    """

    def __init__(self, contains, parent, process_traversal, i=None, filename=None):
        super().__init__(
            contains,
            fieldName=f"[{i}]" if i is not None else "[*]",
            filename=filename,
            parent=parent,
            process_traversal=process_traversal,
        )


class NodeDict(Node):
    """
    A NodeDict is a special Node that contains data in a dict.
    """

    def __init__(self, contains, fieldName, parent, process_traversal, filename=None):
        super().__init__(
            contains,
            fieldName=fieldName,
            filename=filename,
            parent=parent,
            process_traversal=process_traversal,
        )
