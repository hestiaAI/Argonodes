"""
Filters are elements to be applied on models or on Nodes to do a preliminary sorting.

Filters can be used to sort on paths directly, or in a more granular way on the elements of each Node separately.

Basic usage: ``filter = Filter(); model.apply(filter)``
"""
from __future__ import annotations


from operator import contains, eq, ge, gt, le, lt, ne
from re import match


from .helpers import REGEX_SEARCH


LIST_ATTRIBUTES = [
    "path",
    "data",
    "foundType",
    "descriptiveType",
    "unique",
]

LIST_OP = {
    "exact": eq,
    "not": ne,
    "gt": gt,
    "gte": ge,
    "lt": lt,
    "lte": le,
    "contains": contains,
    "startswith": lambda a, b: str(a).startswith(str(b)),
    "endswith": lambda a, b: str(a).endswith(str(b)),
    "isnull": lambda a, _: not a,  # And not "a == None", because we want to check for empty strings as well.
    "regex": lambda a, b: match(b, a),
}

# Need to see if this is useful
ATTRIBUTES_VS_OP = {
    "path": [],
    "data": [],
    "foundType": [],
    "descriptiveType": [],
    "unique": [],
}


def parse_op(string):
    """
    Parse an operation into the correct sub elements.

    :param string: `left__op`.
    :type string: str
    :return: Couple attribute, function.
    :rtype: tuple(str, fun)
    """
    try:
        attribute, op = string.split("__")
    except ValueError:
        raise ValueError("Usage: `parse_op('left__op')``.")

    if attribute not in LIST_ATTRIBUTES:
        print(f"Warning: Attribute `{attribute}` is not a base attribute.")

    if op not in LIST_OP.keys():
        raise ValueError(f"Operation `{op}` is not supported.")

    if ATTRIBUTES_VS_OP[attribute] and op not in ATTRIBUTES_VS_OP[attribute]:
        raise ValueError(f"Operation `{op}` is not supported for attribute `{attribute}`.")

    return attribute, LIST_OP[op]


def get_filters_from_kwargs(kwargs) -> list:
    """
    Returns a complete list of filters.

    :param kwargs: All the filters, in the form `left__op=value`.
    :type kwargs: **dict
    :return: List of filters.
    :rtype: list
    """
    rtn = []
    for attr_op, value in kwargs.items():
        rtn.append((*parse_op(attr_op), value))
    return rtn


class Filter:
    """
    Self-contained (set of) filter(s).

    :param params: List of
    :type params: dict, default None.
    :param targets: If set, the filters will only be applied in the selected paths.
    :type targets: list, default None.
    :param kwargs: All applicable filters, in the form `left__op=value`.
    :type kwargs: **dict
    """

    def __init__(self, params=None, targets=None, filenames=None, **kwargs):
        self.params = params or []
        self.targets = targets or []
        self.filenames = filenames or []
        self.filters = get_filters_from_kwargs(kwargs) or []

    def __repr__(self) -> list:
        return self.filters

    def __call__(self, target, keep_paths=True, keep_root=True):
        from .models import Model
        from .nodes import Node

        if isinstance(target, Node):

            def rec(node):
                if node.children:
                    for children in node.children:
                        rec(children)

                # Keep information in the root part or not.
                if node.path == "$" and keep_root:
                    return

                # Target specific paths or not.
                if self.targets:
                    for target in self.targets:
                        if not REGEX_SEARCH(target).match(node.path):
                            return

                for filtr in self.filters:
                    attr, op, value = filtr

                    # Path is a special case, at it is used as a key.
                    if (attr == "path" and not op(node.path, value)) or (
                        hasattr(node, attr) and not op(getattr(node, attr), value)
                    ):
                        node.delete(remove=not keep_paths)

            rec(target)
        elif isinstance(target, Model):

            def rec(traversal):
                for path in list(traversal.keys()):
                    if "traversal" in traversal[path] and traversal[path]["traversal"]:
                        rec(traversal[path]["traversal"])

                    # Keep information in the root part or not.
                    if path == "$" and keep_root:
                        continue

                    # Target specific paths or not.
                    if self.targets and path not in self.targets:
                        continue

                    for filtr in self.filters:
                        attr, op, value = filtr

                        # Path is a special case, at it is used as a key.
                        if (attr == "path" and not op(path, value)) or (
                            attr in traversal[path] and not op(traversal[path][attr], value)
                        ):
                            # If we want to keep all paths, we only "clean" whatever is inside the Model.
                            if keep_paths:
                                if traversal[path]["traversal"]:
                                    temp = traversal[path]["traversal"]
                                    traversal[path].clear()
                                    traversal[path]["traversal"] = temp
                                else:
                                    del traversal[path]
                            else:
                                pass  # TODO

            for filename, traversal in target.traversal.items():
                if self.filenames and filename not in self.filenames:
                    continue

                rec(traversal)
        else:
            raise ValueError("`item` should be either a Node or a Model.")

        return target

    def select(self, paths):
        """
        Add targets.

        :param paths: Targeted paths.
        :type paths: str or list[str].
        """
        self.add_paths(paths)

    def add_paths(self, paths):
        """
        Add targets.

        :param paths: Targeted paths.
        :type paths: str or list[str].
        """
        if not isinstance(paths, list):
            paths = [paths]

        self.paths.append(paths)

    def filter(self, **kwargs):
        """
        Add filters.

        :param kwargs: Filters to be added.
        :type kwargs: **dict
        """
        self.add(**kwargs)

    def add(self, **kwargs):
        """
        Add filters.

        :param kwargs: Filters to be added.
        :type kwargs: **dict
        """
        self.filters += get_filters_from_kwargs(kwargs)

    def import_filter(self, dct):
        """
        Import filters from a dict.

        :param dct: Dictionary of filters.
        :type dict: dict.
        """
        self.params = dct["params"]
        self.paths = dct["paths"]
        self.filters = dct["filters"]

    def export_filter(self) -> dict:
        """
        Export filters to a dict.

        :return: Dictionary of filters.
        :rtype: dict.
        """
        return {"params": self.params, "paths": self.paths, "filters": self.filters}
