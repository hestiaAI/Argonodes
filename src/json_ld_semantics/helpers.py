"""
Multiple helpers and utils.
"""

from __future__ import annotations


from typing import Union
import re


REGEX_PATH = re.compile(r"\[\d+\]")
REGEX_SEARCH = lambda path: re.compile(
    r"^"
    + path.replace("$", r"\$").replace(".", r"\.").replace("[", r"\[").replace("]", r"\]").replace("*", r".*")
    + r"$"
)


def make_traversal(node) -> None:
    """
    Create the base traversal of a Node, usually a Tree.
    :param node: A given Node, usually a Tree.
    """
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
    node.traversal = void

    assert flatten(node.traversal) == node.get_paths()  # Move to testing in next iteration


def flatten(traversal, keys_only=True) -> Union[set, dict]:
    """
    :param traversal: A given traversal, whether Node or Model.
    :param keys_only: Whether only the keys are important or not.
    :return: Either a set of keys or a flatten dict.
    """
    if keys_only:

        def recur(traversal):
            for k, v in traversal.items():
                yield k
                if v:
                    yield from (r for r in recur(v["traversal"]))

        return set(recur(traversal))
    else:
        ret = {}

        def recur(traversal):
            for path, info in traversal.items():
                yield {
                    path: {
                        "foundType": info["foundType"],
                        "descriptiveType": info["descriptiveType"],
                        "unique": info["unique"],
                        "default": info["default"],
                        "description": info["description"],
                        "example": info["example"],
                        "regex": info["regex"],
                    }
                }
                yield from recur(info["traversal"])

        for r in recur(traversal):
            ret.update(r)
        return ret


# def get_extended_traversal(tree_traversal, raw=False):
#     def recur(inner_tree_traversal):
#         tmp = []
#
#         for key, node in inner_tree_traversal.items():
#             if isinstance(node, NodeList):
#                 tmp.append(node.get_frame(contains="[" + recur(node.traversal) + "]"))
#             else:
#                 if node.traversal:
#                     tmp.append(node.get_frame(contains="[" + recur(node.traversal) + "]"))
#                 else:
#                     tmp.append(node.get_frame())
#
#         tmp = ",".join(tmp).replace("\\", "")
#         return tmp
#
#     if raw:
#         return recur(tree_traversal)
#     else:
#         return json.loads(recur(tree_traversal))


def apply_model(node, model) -> None:
    """
    Apply a Model back to a Node, usually a Tree.
    :param node: A Node, usually a Tree.
    :param model: The Model to be applied.
    """
    flat = model.flatten()

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

    recur(node)


def parse_path(path):
    """
    Parse a JSON path into a list.
    :param path: String, a JSON path.
    :return: List, parsed JSON path.
    """
    return [r for r in re.split("\.|(\[\*\])", path) if r]
