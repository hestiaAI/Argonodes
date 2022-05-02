"""
model.py is everything linked to a model or abstraction of one or multiple files.
"""
from __future__ import annotations


from typing import Optional
import json
import pickle
import re


from deepdiff import DeepDiff


from .default_context import DEFAULT_CONTEXT

# from .filters import parse_op
from .semantics import Tree


def parse_path(path):
    """
    Parse a JSON path into a list.
    :param path: String, a JSON path.
    :return: List, parsed JSON path.
    """
    return [r for r in re.split("\.|(\[\*\])", path) if r]


class Model:
    """
    Model for a specific type of data.
    Internal: Python Dict.
    External: Either JSON or a String.
    """

    def __init__(self, name=None, context=None, filenames=None, traversal=None):
        self.name = name
        self.context = context or DEFAULT_CONTEXT
        self.filenames = filenames or []
        self.traversal = traversal or {}

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return str(self.traversal)

    def add_files(self, filenames) -> Model:
        """
        Add files to parse into the model.
        :param filenames: String or List[String], file paths.
        :return: Self, for chaining.
        """
        if not isinstance(filenames, list):
            filenames = [filenames]

        for filename in filenames:
            try:
                with open(filename, "r", encoding="utf-8"):  # This is for checking the file exists.
                    self.filenames.append(filename)
            except FileNotFoundError:
                print(f"Warning: {filename} could not be opened.")

        return self

    def remove_files(self, filenames) -> Model:
        """
        Remove files to parse into the model.
        :param filenames: String or List[String], file paths.
        :return: Number of files still remaining.
        """
        if not isinstance(filenames, list):
            filenames = [filenames]

        for filename in filenames:
            try:
                self.filenames.remove(filename)
            except ValueError:
                print(f"Warning: {filename} was not found in the list.")

        return self

    def process_files(self, apply=True) -> list:
        """
        Process each file and add to the model traversal.
        :param apply: If True, changes are directly applied to the model; else, changes are not applied.
        :return: List of changes.
        """
        if apply:
            full_traversal = self.traversal
        else:
            full_traversal = self.traversal.copy()
        changes = []

        for filename in self.filenames:
            with open(filename, "r", encoding="utf-8") as file:
                json_data = json.load(file)

            traversal = Tree(json_data).export_traversal()
            changes.append((filename, DeepDiff(full_traversal, traversal)))
            full_traversal.update(traversal)

        return changes

    def get_paths(self) -> set:
        """
        Returns the set of avalaible paths.
        :return: Set[String], set of avalaible paths.
        """

        def recur(traversal):
            for path, info in traversal.items():
                yield path
                yield from recur(info["traversal"])

        return set(recur(self.traversal))

    def find_info(self, target) -> Optional[dict]:
        """
        Returns the given path, or the latest found element within the path.
        :param path: String, a JSON path.
        :return: Dict, the corresponding linked information in the traversal.
        """

        def recur(target, traversal):
            for path, info in traversal.items():
                if path == target:
                    yield info
                if info:
                    yield from (r for r in recur(target, info["traversal"]))

        return next(recur(target, self.traversal))

    def to_list(self, headers=True) -> list:
        """
        Returns the model in the form of a list.
        :param headers: If the first line should be the headers.
        :return: List[List].
        """
        rtn = []
        if headers:
            rtn.append(["path", "foundType", "descriptiveType", "unique", "default", "description", "example", "regex"])

        def recur(traversal):
            for path, info in traversal.items():
                yield [
                    path,
                    info["foundType"],
                    info["descriptiveType"],
                    info["unique"],
                    info["default"],
                    info["description"],
                    info["example"],
                    info["regex"],
                ]
                yield from recur(info["traversal"])

        rtn += [r for r in recur(self.traversal)]

        return rtn

    def flatten(self) -> dict:
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

        for r in recur(self.traversal):
            ret.update(r)
        return ret

    def set_attribute(self, path, **kwargs) -> bool:
        """
        Given a specific path, add more context to that path.
        :param path: String, a valide path.
        :param kwargs:
        :return: True if the path was found and info added; False otherwise.
        """
        info = self.find_info(path)
        if info:
            for attr, value in kwargs.items():
                info[attr] = value
            return True
        return False

    def dump_traversal(self, filename=None, format="pickle"):
        # Formats: pickle, json, markdown
        if format == "pickle":
            if not filename:
                raise ValueError("filename is missing.")
            with open(filename, "wb") as file:
                pickle.dump(self.traversal, file)
        elif format == "json":
            if filename:
                with open(filename, "w") as file:
                    json.dump(self.traversal, file, indent=2, default=str)
            else:
                print(json.dumps(self.traversal, indent=2, default=str))
        elif format == "markdown":
            headers, *liste = self.to_list()
            to_keep = ["path", "foundType", "descriptiveType", "description"]
            indexes = [headers.index(keep) for keep in to_keep]

            temp = []
            for l in liste:
                tmp = [l[index] for index in indexes]
                temp.append(f"| {' | '.join([f'`{tmp[0]}`', tmp[1].__name__, tmp[2] or '/', tmp[3] or '/'])} |")

            markdown = (
                [f"## {self.name or 'Exported Model'}", ""]
                + [f"| {' | '.join(to_keep)} |"]
                + [f"{'|---' * len(to_keep)}|"]
                + temp
            )

            if filename:
                with open(filename, "w") as file:
                    for m in markdown:
                        file.write(f"{m}\n")
            else:
                print("\n".join(markdown))
        else:
            raise ValueError("Incorrect format, please use 'pickle', 'json', 'markdown'.")

    def load_traversal(self, filename):
        with open(filename, "rb") as file:
            self.traversal = pickle.load(file)

    # def filter(self, **kwargs):
    #     if not kwargs:
    #         return self
    #     def recur(traversal, filtr):
    #         attr, op, value = filtr
    #         for path, info in traversal.items():
    #             if info["traversal"]:
    #                 recur(info["traversal"], filtr)
    #             if attr == "path":
    #                 if not op(path, value):
    #                     traversal.pop(path)
    #             else:
    #                 if hasattr(info, attr) and not op(info[attr], value):
    #                     traversal.pop(path)
    #     for attr_op, value in kwargs.items():
    #         filtr = parse_op(attr_op), value
    #         recur(self.traversal, filtr)
    #     return self

    # def _frame_and_context(self) -> dict:
    #     frame_and_context = self.context.copy()
    #     frame_and_context.update(self.frame)
    #
    #     return frame_and_context
    #
    # def export_model(self, text=True, filename=None) -> Optional[str]:
    #     if text:
    #         return json.dumps(self._frame_and_context())
    #     elif filename:
    #         with open(filename, "w", encoding="utf-8") as file:
    #             json.dump(self._frame_and_context(), file, indent=4)
    #         return
