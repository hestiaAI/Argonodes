"""
Models are an abstraction of data sources.

They aim to describe, complete, and enhance the information of unknown data, so that the information related to the data can be re-applied to new data.
"""
from __future__ import annotations


from typing import Optional
import json
import pickle


from deepdiff import DeepDiff


from .applies import apply_model
from .default_context import DEFAULT_CONTEXT
from .helpers import flatten, REGEX_PATH
from .nodes import Tree


class Model:
    """
    Model for a specific type of data.
    Internal: Python Dict.
    External: Either JSON or a String.

    :param name: Name of the Model.
    :type name: str, default None.
    :param context: Context for the JSON-LD export.
    :type context: dict, default None.
    :param filenames: Filenames to be processed by the Model.
    :type filenames: str or list[str], default None.
    :param traversal: A potential existing traversal.
    :type traversal: dict, default None.
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

    def __call__(self, node, rec=True):
        # This will probably get me in purgatory or something.
        """
        Apply a Model back to a Node, usually a Tree.
        :param rec: If False, only current node is modified.
        :param node: A Node, usually a Tree.
        :param model: The Model to be applied.
        """
        flat = self.flatten()

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

    def add_files(self, filenames) -> Model:
        """
        Add files to parse into the model.

        :param filenames: File paths to add.
        :type filenames: str or list[str]
        :return: Self, for chaining.
        :rtype: Model
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

        :param filenames: File paths to remove.
        :type filenames: str or list[str]
        :return: Self, for chaining.
        :rtype: Model
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
        :rtype apply: bool, default True.
        :return: List of changes.
        :rtype: list[str, dict]
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

        :return: Set of avalaible paths.
        :rtype: set[str]
        """

        def recur(traversal):
            for path, info in traversal.items():
                yield path
                yield from recur(info["traversal"])

        return set(recur(self.traversal))

    def find_info(self, target) -> Optional[dict]:
        """
        Returns the given path, or the latest found element within the path.

        :param path: A JSON path.
        :rtype path: str
        :return: The corresponding linked information in the traversal.
        :rtype: dict
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
        :type headers: bool, default True.
        :return: A nice little list representing the Model.
        :rtype: list[list]
        """
        rtn = []
        if headers:
            rtn.append(["path", "foundType", "descriptiveType", "unique", "default", "description", "choices", "regex"])

        def recur(traversal):
            for path, info in traversal.items():
                yield [
                    path,
                    info["foundType"],
                    info["descriptiveType"],
                    info["unique"],
                    info["default"],
                    info["description"],
                    info["choices"],
                    info["regex"],
                ]
                yield from recur(info["traversal"])

        rtn += [r for r in recur(self.traversal)]

        return rtn

    def flatten(self) -> dict:
        """
        Returns a flattened version of the model.

        :return: A dict of the model.
        :rtype: dict
        """
        return flatten(self.traversal, keys_only=False)

    def set_attribute(self, path, **kwargs) -> bool:
        """
        Given a specific path, add more context to that path.

        :param path: A valid path.
        :type path: str
        :param kwargs: The different information to add to that path.
        :type kwargs: Keyworded, variable-length argument list.
        :return: True if the path was found and info added; False otherwise.
        :rtype: bool
        """
        info = self.find_info(path)
        if info:
            for attr, value in kwargs.items():
                info[attr] = value
            return True
        return False

    def dump_traversal(self, filename=None, scheme="pickle") -> None:
        """
        Dump the traversal in different format.

        :param filename: If None, will print in the given format.
        :type filename: str, default None.
        :param scheme: Can be either `pickle`, `json`, `markdown`.
        :type scheme: str, default "pickle".
        """
        if scheme == "pickle":
            if not filename:
                raise ValueError("filename is missing.")
            with open(filename, "wb") as file:
                pickle.dump(self.traversal, file)
        elif scheme == "json":
            if filename:
                with open(filename, "w") as file:
                    json.dump(self.traversal, file, indent=2, default=str)
            else:
                print(json.dumps(self.traversal, indent=2, default=str))
        elif scheme == "markdown":
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

    def load_traversal(self, filename) -> None:
        """
        Load a format from a pickle.

        :param filename: Path to a pickled format.
        :type filename: str
        """
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
