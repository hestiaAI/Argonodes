"""
Models are an abstraction of data sources.

They aim to describe, complete, and enhance the information of unknown data, so that the information related to the data can be re-applied to new data.

Basic usage = ``model = Model(tree)``
"""
from __future__ import annotations


from typing import Optional
import json
import pickle


from deepdiff import DeepDiff


from .default_context import DEFAULT_CONTEXT
from .helpers import ATTRS_EXPORT, ATTRS_MARKDOWN, ATTRS_MODEL_TO_NODE, flatten, REGEX_PATH


class Model:
    """
    Model for a specific type of data.

    :param trees: Trees to be processed by the Model.
    :type trees: Tree or list[Tree], default None.
    :param name: Name of the Model.
    :type name: str, default None.
    :param context: Context for the JSON-LD export.
    :type context: dict, default None.
    """

    def __init__(self, trees=None, name=None, context=None):
        self.name = name
        self.context = context or DEFAULT_CONTEXT
        self.traversal = {}
        self.changes = []
        self.num_changes = 0

        if trees:
            if not isinstance(trees, list):
                trees = [trees]

            for tree in trees:
                self.add_tree(tree)

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
        self.add_traversal(tree.export_traversal(), apply=apply)

    def add_traversal(self, traversal, apply=True) -> None:
        """
        Add a traversal to the Model.

        :param traversal: The traversal, from a Tree.
        :type traversal: dict
        :param apply: If True, will effectively be applied to the Model.
        :type apply: bool
        """
        if apply:
            full_traversal = self.traversal
        else:
            full_traversal = self.traversal.copy()

        full_traversal.update(traversal)
        self.num_changes += 1

        self.changes.append((self.num_changes, apply, DeepDiff(full_traversal, traversal)))

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
            rtn.append(ATTRS_EXPORT)

        def recur(traversal):
            for path, info in traversal.items():
                yield [path] + [info[attr] for attr in info.keys() if attr in ATTRS_EXPORT and attr != "path"]
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

    def export_traversal(self, filename=None, scheme="pickle") -> None:
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
            to_keep = ATTRS_MARKDOWN
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
