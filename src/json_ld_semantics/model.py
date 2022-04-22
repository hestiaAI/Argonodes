"""
model.py is everything linked to a model or abstraction of one or multiple files.
"""
from typing import Optional
import json
import re


from deepdiff import DeepDiff


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

    def __init__(self, context=None, filenames=None, traversal=None, frame=None):
        if context:
            self.context = context
        else:
            self.context = None  # DEFAULT_CONTEXT

        if filenames:
            self.filenames = filenames
        else:
            self.filenames = []

        if traversal:
            self.traversal = traversal
        else:
            self.traversal = {}

        if frame:
            self.frame = frame
        else:
            self.frame = {}

    def add_files(self, filenames) -> int:
        """
        Add files to parse into the model.
        :param filenames: String or List[String], file paths.
        :return: Number of files effectively added.
        """
        if not isinstance(filenames, list):
            filenames = [filenames]

        for filename in filenames:
            try:
                with open(filename, "r", encoding="utf-8"):  # This is for checking the file exists.
                    self.filenames.append(filename)
            except FileNotFoundError:
                print(f"Warning: {filename} could not be opened.")

        return len(self.filenames)

    def remove_files(self, filenames) -> int:
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

        return len(self.filenames)

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

        # def recur(traversal, target) -> Optional[dict]:
        #     for path, info in traversal.items():
        #         print(path)
        #         if path == target:
        #             return info
        #         else:
        #             return recur(info["traversal"], target)
        #     return None
        #
        # return recur(self.traversal, target)

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

    def _frame_and_context(self) -> dict:
        frame_and_context = self.context.copy()
        frame_and_context.update(self.frame)

        return frame_and_context

    def export_model(self, text=True, filename=None) -> Optional[str]:
        if text:
            return json.dumps(self._frame_and_context())
        elif filename:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(self._frame_and_context(), file, indent=4)
            return
