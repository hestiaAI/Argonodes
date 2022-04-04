import json
from typing import Optional
from deepdiff import DeepDiff
from .semantics import Tree
import re


def parse_path(path):
    return [r for r in re.split("\.|(\[\*\])", path) if r]


class Model:
    """
    Model for a data frame.
    Internal: Python Dict.
    External: Either JSon or a String.
    """

    def __init__(self, context=None, filenames=None, traversal=None, frame=None, multiple=True):
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

        self.multiple = multiple

    def add_files(self, filenames) -> int:
        if not isinstance(filenames, list):
            filenames = [filenames]

        for filename in filenames:
            try:
                with open(filename, "r"):  # This is for checking the file exists.
                    self.filenames.append(filename)
            except FileNotFoundError:
                print(f"Warning: {filename} could not be opened.")

        return len(self.filenames)

    def remove_files(self, filenames) -> int:
        if not isinstance(filenames, list):
            filenames = [filenames]

        for filename in filenames:
            try:
                self.filenames.remove(filename)
            except ValueError as e:
                print(f"Warning: {filename} was not found in the list.")

        return len(self.filenames)

    def process_files(self, apply=True) -> list:
        if apply:
            full_traversal = self.traversal
        else:
            full_traversal = self.traversal.copy()
        changes = []

        for filename in self.filenames:
            with open(filename, "r") as f:
                json_data = json.load(f)

            traversal = Tree(json_data).export_traversal()
            changes.append((filename, DeepDiff(full_traversal, traversal)))
            full_traversal.update(traversal)

        return changes

    def get_paths(self) -> set:
        def recur(traversal):
            for key, info in traversal.items():
                yield info["path"]
                yield from recur(info["traversal"])

        return set(recur(self.traversal))

    def find_info(self, path):
        """
        Returns the given path, or the latest found element within the path.
        :param path: String, a JSON path.
        :return: The corresponding linked information in the traversal.
        """
        def recur(traversal, liste):
            for key, info in traversal.items():
                if key == liste[0]:
                    if info["traversal"] and liste[1:]:
                        return recur(info["traversal"], liste[1:])
                    else:
                        return info
            return None

        return recur(self.traversal, parse_path(path))

    def to_list(self, headers=True) -> list:
        rtn = []
        if headers:
            rtn.append(
                [
                    "path",
                    "foundType",
                    "descriptiveType",
                    "unique",
                    "default",
                    "description",
                    "example",
                    "regex"
                ]
            )

        def recur(traversal):
            for key, info in traversal.items():
                yield [
                    info["path"],
                    info["foundType"],
                    info["descriptiveType"],
                    info["unique"],
                    info["default"],
                    info["description"],
                    info["example"],
                    info["regex"],
                ]
                yield from recur(info["traversal"])

        rtn.append(list(recur(self.traversal)))

        return rtn

    def set_attribute(self, path, **kwargs) -> None:
        info = self.find_info(path)
        for k, v in kwargs.items():
            info[k] = v

    # def apply_self_traversal(self):
    #     self.frame = get_extended_traversal(traversal=self.traversal)

    def _frame_and_context(self) -> dict:
        frame_and_context = self.context.copy()
        frame_and_context.update(self.frame)

        return frame_and_context

    def export_model(self, text=True, filename=None) -> Optional[str]:
        if text:
            return json.dumps(self._frame_and_context())
        elif filename:
            with open(filename, "w") as file:
                json.dump(self._frame_and_context(), filename, indent=4)
            return
