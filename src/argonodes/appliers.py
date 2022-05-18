"""
Appliers are functions or objects passed as parameters to a Node to allow modifications, additions, or exploration on the data of the Node, and/or its children.

The idea is identical to that of the Visitor pattern. There are two types of Appliers: Appliers that add/modify existing attributes in the Node, and Appliers that extract attributes from the Node. These Appliers are respectively functions and objects.
"""

from __future__ import annotations


from collections import Counter, defaultdict
import uuid


from .helpers import flatten, REGEX_PATH, REGEX_SEARCH


class DistinctValues:
    """
    Standalone Applier to check all distinct values for Nodes.

    It is possible to sort the values by frequency or by path, in ascending or descending order. Once applied, this Applier keeps in memory the repetitions of values and children for the targeted Nodes. It is possible to retrieve them either with `self.data`, or with dedicated functions for more granularity.

    :param sort: How to sort the gathered values.
    :type sort: str, either `key` or `count`.
    :param reverse: Whether to reverse the sorting order or not.
    :type reverse: bool, default None.
    """

    def __init__(self, sort="count", reverse=None) -> None:
        self._data = defaultdict(lambda: {"description": "", "children": Counter(), "data": Counter()})
        if sort not in ["key", "count"]:
            raise ValueError("`sort` can be either `key` or `count`.")
        self.sort = sort
        self.reverse = reverse

    def __call__(self, node, rec=True) -> None:
        if not rec:
            raise AssertionError("Distinct values on a single Node are not useful.")

        def recur(node):
            path = REGEX_PATH.sub("[*]", node.path)

            if hasattr(node, "data"):
                if node.data:
                    self._data[path]["data"][node.data] += 1

            if node.children:
                for children in node.children:
                    children_path = REGEX_PATH.sub("[*]", children.path)
                    self._data[path]["children"][children_path] += 1
                    recur(children)

        recur(node)

    @property
    def data(self) -> dict:
        """
        Raw data. Immutable.

        :return: Raw data.
        :rtype: dict
        """
        srt = 1 if self.sort == "count" else 0
        rvrs = self.reverse or True if self.sort == "count" else False

        return {
            k: {
                "description": v["description"],
                "children": dict(sorted(v["children"].items(), key=lambda item: item[srt], reverse=rvrs)),
                "data": dict(sorted(v["data"].items(), key=lambda item: item[srt], reverse=rvrs)),
            }
            for k, v in self._data.items()
        }

    @data.setter
    def data(self, value) -> None:
        raise AttributeError("Cannot set `data`.")

    def sort(self, sort, reverse=None) -> None:
        """
        Change the sorting order.

        :param sort: How to sort the gathered values.
        :type sort: str, either `key` or `count`.
        :param reverse: Whether to reverse the sorting order or not.
        :type reverse: bool, default None.
        """
        if sort not in ["key", "count"]:
            raise ValueError("`sort` can be either `key` or `count`.")
        self.sort = sort
        self.reverse = reverse

    def get_found_values(self) -> dict:
        """
        Return the values only.

        :return: A dictionary with the paths and the corresponding values.
        :rtype: dict
        """
        return {k: dict(v["data"]) for k, v in self.data.items()}

    def get_recurring_values(self, threshold=2) -> dict:
        """
        Return the values only, filtered on a given threshold.

        :param threshold: How many times the value should occur to be considered as "recurring".
        :type threshold: int, default 2.
        :return: A dictionary with the paths and the corresponding values, filtered on a given threshold.
        :rtype: dict
        """
        return {k: {k2: v2 for k2, v2 in dict(v["data"]).items() if v2 >= threshold} for k, v in self.data.items()}

    def to_list(self) -> list:
        """
        Return a flattened version of data.

        :return: A flattened version of data.
        :rtype: list
        """
        return [["path", "description", "possible_children", "possible_values"]] + [
            [k, v["description"], list(set(v["children"])), list(set(v["data"]))] for k, v in self.data.items()
        ]


class FoundRegex:
    """
    This standalone Applier will try to find a matching regex for each targeted Node.

    It will try to find a uniquely matching regex for each targeted Node, based on the recurring values of that one. A failure to do so will result in a list of potential regex that may cover all the found cases. It is possible to retrieve them with `self.data`.

    Note that this Applier makes use of another Applier, `DistinctValues`.

    Warning, it uses an external package that you should install first: `pip install tdda`.
    """

    def __init__(self) -> None:
        self.distinct_values = DistinctValues()
        self._data = defaultdict(lambda: {"description": "", "data": [], "regex": None, "unique": True})

    def __call__(self, node, rec=True) -> None:
        from tdda.rexpy.rexpy import Extractor

        self.distinct_values(node, rec=rec)

        for path, info in self.distinct_values.data.items():
            try:
                regex = Extractor({str(k): v for k, v in info["data"].items()}).results.rex

                if len(regex) == 1:
                    regex = regex[0]
                    unique = True
                else:
                    unique = False

                self.data[path] = {
                    "description": info["description"],
                    "data": info["data"],
                    "regex": regex,
                    "unique": unique,
                }
            except AttributeError:
                continue

        return

    @property
    def data(self) -> dict:
        """
        Raw data. Immutable.

        :return: Raw data.
        :rtype: dict
        """
        return self._data

    @data.setter
    def data(self, value) -> None:
        raise AttributeError("Cannot set `data`.")


def make_traversal(node, rec=True) -> None:
    """
    Create the base traversal of a Node, usually a Tree.

    :param node: A given Node, usually a Tree.
    :type node: Node
    :param rec: Must be True.
    :type rec: bool, default True.
    """
    if not rec:
        raise AssertionError("Cannot make traversal not recursively.")

    void = {}

    def recur(node, void) -> None:
        ignored = hasattr(node, "ignore") and node.ignore

        path = REGEX_PATH.sub("[*]", node.path)
        if ignored:
            path = uuid.uuid5(uuid.NAMESPACE_URL, path)

        if path not in void:
            if ignored:
                void[path] = {
                    "traversal": {},
                }
            else:
                void[path] = {
                    "foundType": node.foundType,
                    "descriptiveType": node.descriptiveType,
                    "unique": node.unique,
                    "default": node.default,
                    "description": node.description,
                    "choices": node.choices,
                    "regex": node.regex,
                    "traversal": {},
                }

        if node.children:
            for children in node.children:
                recur(children, void[path]["traversal"])
        else:
            return

    recur(node, void)
    node.traversal = void

    assert flatten(node.traversal) == node.get_paths()  # Move to testing in next iteration


def ignore_node(node, rec=False, paths=None) -> None:
    """
    Marks every targeted Node as "ignored" - subsequent functions shall take that into account for further actions (e.g., export).

    :param node: A given Node, usually a Tree.
    :type node: Node
    :param rec: If True, the function shall be applied on all children.
    :type rec: bool, default True.
    :param paths: What are the targeted paths.
    :type paths: List[str] or str.
    """
    if paths and not isinstance(paths, list):
        paths = [paths]

    def apply_to(node):
        if paths:
            for path in paths:
                if REGEX_SEARCH(path).match(node.path):
                    node.ignore = True
        else:
            node.ignore = True

    def recur(node):
        apply_to(node)
        if node.children:
            for children in node.children:
                recur(children)

    if paths and rec:
        recur(node)
    else:
        apply_to(node)

    return
