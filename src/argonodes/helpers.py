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


ATTRS_NODE_ONLY = ["fieldName", "data", "parent", "children", "traversal", "filename"]
ATTRS_EXPORT = ["path", "foundType", "descriptiveType", "unique", "default", "description", "choices", "regex"]
ATTRS_MODEL_TO_NODE = ["descriptiveType", "unique", "default", "description", "choices", "regex"]
ATTRS_MARKDOWN = ["path", "foundType", "descriptiveType", "description"]


def flatten(traversal, keys_only=True) -> set | dict:
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
                        "choices": info["choices"],
                        "regex": info["regex"],
                    }
                }
                yield from recur(info["traversal"])

        for r in recur(traversal):
            ret.update(r)
        return ret


def parse_path(path) -> list:
    """
    Parse a JSON path into a list.

    :param path: A JSON path.
    :type path: str
    :return: Parsed JSON path.
    :rtype: list
    """
    return [r for r in re.split("\.|(\[\*\])", path) if r]
