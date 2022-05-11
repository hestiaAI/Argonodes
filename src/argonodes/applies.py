from __future__ import annotations


from collections import Counter
from typing import Any, Union


from .helpers import flatten, REGEX_PATH


def base_apply(node, rec=True, *args, **kwargs) -> Union[None, Any]:
    """
    This base method is an example and should not be used.
    :param node: A given Node, usually a Tree.
    :param rec: If True, the function shall be applied on all children.
    :param args: Add. args.
    :param kwargs: Add. kwargs.
    :return: Either nothing, or whatever makes sense.
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
        node.example = info["example"]
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
