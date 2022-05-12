from __future__ import annotations


from collections import Counter, defaultdict


from .helpers import flatten, REGEX_PATH


def base_apply(node, rec=True, *args, **kwargs) -> None:
    """
    This base method is an example and should not be used.
    :param node: A given Node, usually a Tree.
    :param rec: If True, the function shall be applied on all children.
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
    :param rec: Must be True.
    """
    if not rec:
        raise AssertionError("Cannot make traversal not recursively.")

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
    def __init__(self):
        self._data = defaultdict(lambda: {"children": Counter(), "data": Counter()})

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
        return {k: {"children": dict(v["children"]), "data": dict(v["data"])} for k, v in self._data.items()}

    @data.setter
    def data(self, value):
        raise AttributeError("Cannot set `data`.")

    def get_found_values(self):
        return {k: dict(v["data"]) for k, v in self.data.items()}

    def get_recurring_values(self, threshold=2):
        return {k: {k2: v2 for k2, v2 in dict(v["data"]).items() if v2 >= threshold} for k, v in self.data.items()}
