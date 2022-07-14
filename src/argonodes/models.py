"""
Models are an abstraction of data sources.

They aim to describe, complete, and enhance the information of unknown data, so that the information related to the data can be re-applied to new data.

Basic usage = ``model = Model(tree)``
"""
from __future__ import annotations


from collections import defaultdict
from typing import Any, Generator, List, Optional, Set, Tuple
import csv
import json
import os
import pickle


from deepdiff import DeepDiff


from .default_context import DEFAULT_CONTEXT
from .helpers import ATTRS_EXPORT, ATTRS_MARKDOWN, ATTRS_MODEL_TO_NODE, flatten, REGEX_PATH
from .nodes import NA, Root


class Model:
    """
    Model for a specific type of data.

    If multiple files are used, the model will internally use the file names as key for traversals.
    Else, a default None key is used.

    :param trees: Trees to be processed by the Model.
    :type trees: Tree or list[Tree], default None.
    :param name: Name of the Model.
    :type name: str, default None.
    :param context: Context for the JSON-LD export.
    :type context: dict, default None.
    """

    def __init__(self, trees=None, name=None, context=None):
        self.name = name or "Argonode Model"
        self.context = context or DEFAULT_CONTEXT
        self.traversal = defaultdict(dict)
        self.changes = []
        self.num_changes = 0

        if trees:
            try:
                for tree in trees:
                    self.add_tree(tree)
            except:
                self.add_tree(trees)

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
        filename = node.filename
        flat = flatten(self.traversal[filename], keys_only=False)

        def apply_to(node):
            path = REGEX_PATH.sub("[*]", node.path)
            info = flat[path]

            for attr in info.keys():
                if attr in ATTRS_MODEL_TO_NODE:
                    setattr(node, attr, info[attr])

        def recur(node):
            apply_to(node)
            if node.children:
                for children in node.children:
                    recur(children)

        if rec:
            recur(node)
        else:
            apply_to(node)

    def add_tree(self, tree, apply=True) -> None:
        """
        Add a Tree's traversal to the Model.

        :param tree: A Tree.
        :type tree: Tree
        :param apply: If True, will effectively be applied to the Model.
        :type apply: bool
        """
        self.add_traversal(tree.export_traversal(), filename=tree.filename, apply=apply)

    def add_traversal(self, traversal, filename=None, apply=True) -> None:
        """
        Add a traversal to the Model.

        :param traversal: The traversal, from a Tree.
        :type traversal: dict
        :param filename: The filename, from a Tree.
        :type filename: str, default None.
        :param apply: If True, will effectively be applied to the Model.
        :type apply: bool, default True.
        """
        traversal_copy = self.traversal.copy()

        if apply:
            self.traversal[filename].update(traversal)  # And yes, it works even when filename=None!
            self.changes.append((self.num_changes, apply, DeepDiff(traversal_copy, self.traversal)))
        else:
            traversal_copy[filename].update(traversal)  # Tout pareil !
            self.changes.append((self.num_changes, apply, DeepDiff(self.traversal, traversal_copy)))

        self.num_changes += 1

    def get_paths(self) -> dict:
        """
        Returns the set of avalaible paths.

        :return: Set of avalaible paths.
        :rtype: set[str]
        """

        def recur(traversal):
            for path, info in traversal.items():
                yield path
                yield from recur(info["traversal"])

        return {filename: set(recur(traversal)) for filename, traversal in self.traversal.items()}

    def find_info(self, target, filename=None) -> Optional[dict]:
        """
        Returns the given path, or the latest found element within the path.

        :param target: A JSON path.
        :rtype target: str
        :param filename: Filename.
        :rtype filename: str, default None.
        :return: The corresponding linked information in the traversal.
        :rtype: dict
        """

        def recur(target, traversal):
            for path, info in traversal.items():
                if path == target:
                    yield info
                if info:
                    yield from (r for r in recur(target, info["traversal"]))

        return next(recur(target, self.traversal[filename]))

    def to_list(self, headers=True) -> tuple[list, dict] | dict:
        """
        Returns the model in the form of a list.

        :param headers: If the first line should be the headers.
        :type headers: bool, default True.
        :return: A nice little list representing the Model.
        :rtype: list[list]
        """

        def recur(traversal):
            for path, info in traversal.items():
                temp = []
                for attr in info.keys():
                    if attr in ATTRS_EXPORT and attr != "path":
                        if "<class " in str(info[attr]):
                            temp.append(info[attr].__name__)
                        else:
                            temp.append(str(info[attr]))
                yield [
                    path
                ] + temp  # [str(info[attr]) for attr in info.keys() if attr in ATTRS_EXPORT and attr != "path"]
                yield from recur(info["traversal"])

        rtn = {filename: [r for r in recur(traversal)] for filename, traversal in self.traversal.items()}

        if headers:
            return ATTRS_EXPORT, rtn
        else:
            return rtn

    def flatten(self) -> dict:
        """
        Returns a flattened version of the model.

        :return: A dict of the model.
        :rtype: dict
        """
        return {filename: flatten(traversal, keys_only=False) for filename, traversal in self.traversal.items()}

    def set_attributes(self, path, filename=None, **kwargs) -> bool:
        """
        Given a specific path, add more context to that path.

        :param path: A valid path.
        :type path: str
        :param filename: A filename.
        :type filename: str, default None.
        :param kwargs: The different information to add to that path.
        :type kwargs: Keyworded, variable-length argument list.
        :return: True if the path was found and info added; False otherwise.
        :rtype: bool
        """
        info = self.find_info(path, filename)
        if info:
            for attr, value in kwargs.items():
                info[attr] = value
            return True
        return False

    def export_to_csv(self, filename):
        """
        Sugar for argonodes.exporters.CSVExporter.

        :param filename: Filename where to export.
        :type filename: str
        """
        from .exporters import CSVExporter

        exporter = CSVExporter(filename)
        exporter(self)

    def export_to_pickle(self, filename):
        """
        Sugar for argonodes.exporters.PickleExporter.

        :param filename: Filename where to export.
        :type filename: str
        """
        from .exporters import PickleExporter

        exporter = PickleExporter(filename)
        exporter(self)

    def export_to_markdown(self, filename=None):
        """
        Sugar for argonodes.exporters.MarkdownExporter.

        :param filename: Filename where to export. If None, it will print the Markdown instead.
        :type filename: str, default None.
        """
        from .exporters import PickleExporter

        exporter = PickleExporter(filename)
        exporter(self)

    def import_from_csv(self, filename):
        """
        Import a Model from CSV.

        :param filename: Filename where to import.
        :type filename: str
        """
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                filename, path = row.pop("path").split(":")
                if filename == "":
                    filename = None
                for k, v in row.items():
                    if v == "RootNode":
                        row[k] = Root
                    if v == "N/A":
                        row[k] = NA
                    if v == "None":
                        row[k] = None
                self.set_attributes(path, filename=filename, **row)

    def import_from_pickle(self, filename):
        """
        Import a Model from a Pickle.

        :param filename: Filename where to import.
        :type filename: str
        """
        with open(filename, "rb") as file:
            self.traversal = pickle.load(file)

    def apply(self, filtr) -> Model:
        """
        Apply a Filter to the Model.

        :param filtr: The Filter.
        :type filtr: Filter
        :return: Self, for chaining.
        :rtype: Model
        """
        filtr(self)

        return self
