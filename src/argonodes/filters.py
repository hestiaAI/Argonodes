"""
Filters are elements to be applied on models or on Nodes to do a preliminary sorting.

Filters can be used to sort on paths directly, or in a more granular way on the elements of each Node separately.

Basic usage: ``filter = Filter(); model.apply(filter)   ``
"""

from operator import contains, eq, ge, gt, le, lt, ne
from re import match


from .helpers import REGEX_SEARCH
from .nodes import Node


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
    "startswith": lambda a, b: str(b).startswith(str(a)),
    "endswith": lambda a, b: str(b).endswith(str(a)),
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

    :param string:
    :type string:
    :return: Couple attribute, function.
    :rtype: tuple(str, fun)
    """
    try:
        attribute, op = string.split("__")
    except ValueError:
        raise ValueError("Usage: `parse_op('left__op')` or `parse_op('left__in__op')`.")

    if attribute not in LIST_ATTRIBUTES:
        print(f"Warning: Attribute `{attribute}` is not a base attribute.")

    if op not in LIST_OP.keys():
        raise ValueError(f"Operation `{op}` is not supported.")

    if ATTRIBUTES_VS_OP[attribute] and op not in ATTRIBUTES_VS_OP[attribute]:
        raise ValueError(f"Operation `{op}` is not supported for attribute `{attribute}`.")

    return attribute, LIST_OP[op]


def get_filters_from_kwargs(kwargs) -> list:
    """
    Doc TODO

    :param kwargs:
    :return:
    :rtype: list
    """
    rtn = []
    for attr_op, value in kwargs.items():
        rtn.append((*parse_op(attr_op), value))
    return rtn


class Filter:
    """
    Doc TODO

    :param model:
    :type model:
    :param params:
    :type params:
    :param paths:
    :type paths:
    :param filters:
    :type filters:
    """

    def __init__(self, params=None, targets=None, **kwargs):
        self.params = params or []
        self.targets = targets or []
        self.filters = get_filters_from_kwargs(kwargs) or []

    def __repr__(self) -> list:
        return self.filters

    def __call__(self, model):
        def rec(traversal):
            for path, info in traversal.items():
                if "traversal" in info and info["traversal"]:
                    rec(info["traversal"])

            for filtr in self.filters:
                attr, op, value = filtr

                for path in list(traversal.keys()):
                    if self.targets and path not in self.targets:
                        continue

                    if attr == "path":
                        if not op(path, value):
                            del traversal[path]
                        else:
                            pass
                            # ???
                    else:
                        info = traversal[path]
                        if attr in info and not op(info[attr], value):
                            del traversal[path]
                        else:
                            pass
                            # ???

        rec(model.traversal)

        return model

    def select(self, paths):
        """
        Doc TODO

        :param paths:
        :type paths:
        """
        self.add_paths(paths)

    def add_paths(self, paths):
        """
        Doc TODO

        :param paths:
        :type paths:
        """
        if not isinstance(paths, list):
            paths = [paths]

        self.paths.append(paths)

    def filter(self, **kwargs):
        """
        Doc TODO

        :param kwargs:
        :type kwargs:
        """
        self.add(**kwargs)

    def add(self, **kwargs):
        """
        Doc TODO

        :param kwargs:
        :type kwargs:
        """
        self.filters += get_filters_from_kwargs(kwargs)

    def import_filter(self, dct):
        """
        Doc TODO

        :param dct:
        :type dict:
        """
        self.paths = dct["paths"]
        self.filters = dct["filters"]

    def export_filter(self) -> dict:
        """
        Doc TODO

        :return:
        :rtype: dict
        """
        return {"paths": self.paths, "filters": self.filters}
