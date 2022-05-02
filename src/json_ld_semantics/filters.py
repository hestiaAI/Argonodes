from operator import contains, eq, ge, gt, le, lt, ne
from re import match


from .semantics import Node


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
    try:
        attribute, op = string.split("__")
    except ValueError:
        raise ValueError("Usage: parse_op('left__op').")

    if attribute not in LIST_ATTRIBUTES:
        raise ValueError(f"Attribute `{attribute}` is not supported.")

    if op not in LIST_OP.keys():
        raise ValueError(f"Operation `{op}` is not supported.")

    if ATTRIBUTES_VS_OP[attribute] and op not in ATTRIBUTES_VS_OP[attribute]:
        raise ValueError(f"Operation `{op}` is not supported for attribute `{attribute}`.")

    return attribute, LIST_OP[op]


def get_filters_from_kwargs(kwargs) -> list:
    rtn = []
    for attr_op, value in kwargs.items():
        rtn.append((*parse_op(attr_op), value))
    return rtn


class Filter:
    def __init__(self, model, **kwargs):
        self.model = model
        self.filters = get_filters_from_kwargs(kwargs) or []

    def __repr__(self) -> list:
        return self.filters

    def filter(self, **kwargs):
        self.add(**kwargs)

    def add(self, **kwargs):
        self.filters += get_filters_from_kwargs(kwargs)

    def __call__(self, node):
        if not isinstance(node, Node):
            raise ValueError("Should use type node.")

        node.apply(self)

        return node
