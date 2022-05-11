from __future__ import annotations


from collections import Counter, defaultdict
from typing import Any, Union


from .helpers import flatten, REGEX_PATH
from .nodes import NodeDict, NodeList, Tree


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


def apply_model(node, rec, model) -> None:
    """
    Apply a Model back to a Node, usually a Tree.
    :param rec: If False, only current node is modified.
    :param node: A Node, usually a Tree.
    :param model: The Model to be applied.
    """
    flat = model.flatten()

    def apply_to(node):
        path = REGEX_PATH.sub("[*]", node.path)
        info = flat[path]
        node.descriptiveType = info["descriptiveType"]
        node.unique = info["unique"]
        node.default = info["default"]
        node.description = info["description"]
        node.choices = info["choices"]
        node.regex = info["regex"]

    def recur(node):
        apply_to(node)
        if node.children:
            for children in node.children:
                recur(children)

    if rec:
        recur(node)
    else:
        apply_to(node)


# def find_distinct_values(node, rec=True, result=None) -> None:
#     if not rec:
#         raise AssertionError("Distinct values on single node not useful.")
#
#     result = defaultdict(Counter)
#
#     def recur(node):
#         path = REGEX_PATH.sub("[*]", node.path)
#
#         if hasattr(node, "data") and node.data:
#             result[path][node.data] += 1
#
#         if node.children:
#             for children in node.children:
#                 children_path = REGEX_PATH.sub("[*]", children.path)
#                 result[node.fieldName][f"children: {children_path}"] += 1
#                 recur(children)
#
#     recur(node)
#
#     for k, v in result.items():
#         print(k)
#         print(v)
#         break
#     return
#
#     print(result)
