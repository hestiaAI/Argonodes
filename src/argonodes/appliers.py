from __future__ import annotations


from collections import Counter, defaultdict
import uuid


from .helpers import flatten, REGEX_PATH, REGEX_SEARCH


def base_apply(node, rec=True, *args, **kwargs) -> None:
    """
    This base method is an example and should not be used.

    :param node: A given Node, usually a Tree.
    :type node: Node
    :param rec: If True, the function shall be applied on all children.
    :type rec: bool, default True.
    :param args: Add. args.
    :param kwargs: Add. kwargs.
    :return: Nothing, because applies should be chained.
    """

    def apply_to(node):
        pass

    def recur(node):
        apply_to(node)
        if node.children:
            for children in node.children:
                recur(children)

    if rec:
        recur(node)
    else:
        apply_to(node)

    return


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


class DistinctValues:
    def __init__(self, sort="count", reverse=None):
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
    def data(self):
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
    def data(self, value):
        raise AttributeError("Cannot set `data`.")

    def sort(self, sort):
        if sort not in ["key", "count"]:
            raise ValueError("`sort` can be either `key` or `count`.")
        self.sort = sort

    def get_found_values(self):
        return {k: dict(v["data"]) for k, v in self.data.items()}

    def get_recurring_values(self, threshold=2):
        return {k: {k2: v2 for k2, v2 in dict(v["data"]).items() if v2 >= threshold} for k, v in self.data.items()}

    def to_list(self) -> list:
        return [["path", "description", "possible_children", "possible_values"]] + [
            [k, v["description"], list(set(v["children"])), list(set(v["data"]))] for k, v in self.data.items()
        ]


def ignore_node(node, rec=False, paths=None):
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