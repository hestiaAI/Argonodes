"""
Exporters are useful to export Models in multiple formats.

In some cases, it may be necessary to export in formats that do not correspond to the basic Argonodes format (e.g., CSV, SQL, ...). It is therefore possible to build custom exporters that meet these needs.

Basic usage: ``exporter = Exporter(); model.export(exporter)``
"""
from abc import ABC, abstractmethod
import csv
import json
import mimetypes
import os
import pickle


from .helpers import ATTRS_EXPORT, ATTRS_MARKDOWN
from .nodes import NA


class Exporter(ABC):
    """
    Abstraction for every Exporter
    """

    EXT = ""

    def __init__(self, filename):
        _, ext = os.path.splitext(filename)
        if ext != self.EXT:
            filename += self.EXT
            print(
                f"Warning: {self.EXT} will automatically be added at the end of the file name.\nResult will thus be {filename}."
            )
        self.filename = filename

    @abstractmethod
    def __call__(self, model):
        pass


class PickleExporter(Exporter):
    """
    Exporter to a Python Pickle.

    :param filename: Filename where to export.
    :type filename: str
    """

    EXT = ".pickle"

    def __init__(self, filename):
        super().__init__(filename)

    def __call__(self, model):
        with open(self.filename, "wb") as file:
            pickle.dump(model.traversal, file)


class JSONExporter(Exporter):
    """
    Exporter to JSON.

    :param filename: Filename where to export. If None, it will print the JSON instead.
    :type filename: str, default None.
    """

    EXT = ".json"

    def __init__(self, filename=None):
        if filename:
            super().__init__(filename)
        else:
            self.filename = None

    def __call__(self, model):
        if self.filename:
            with open(self.filename, "w") as file:
                json.dump(model.traversal, file, indent=2, default=str)
        else:
            print(json.dumps(model.traversal, indent=2, default=str))


class MarkdownExporter(Exporter):
    """
    Exporter to Markdown.

    :param filename: Filename where to export. If None, it will print the Markdown instead.
    :type filename: str, default None.
    """

    EXT = ".md"

    def __init__(self, filename=None):
        if filename:
            super().__init__(filename)
        else:
            self.filename = None

    def __call__(self, model):
        headers, listes = model.to_list()
        to_keep = ATTRS_MARKDOWN
        indexes = [headers.index(keep) for keep in to_keep]

        markdown = [f"## {model.name or 'Exported Argonode Model'}", ""]

        for filename, liste in listes.items():
            temp = []
            for l in liste:
                tmp = [l[index] for index in indexes]
                temp.append(f"| {' | '.join(tmp)} |")

            markdown += (
                [f"### {f'`{filename}`' if filename else '(unspecified file)'}", ""]
                + [f"| {' | '.join(to_keep)} |"]
                + [f"{'|---' * len(to_keep)}|"]
                + temp
                + [""]
            )

        if self.filename:
            with open(self.filename, "w") as file:
                for m in markdown:
                    file.write(f"{m}\n")
        else:
            print("\n".join(markdown))


class CSVExporter(Exporter):
    """
    Exporter to a CSV.

    :param filename: Filename where to export.
    :type filename: str
    """

    EXT = ".csv"

    def __init__(self, filename):
        super().__init__(filename)

    def __call__(self, model):
        headers, listes = model.to_list()

        with open(self.filename, "w") as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(headers)
            for filename, liste in listes.items():
                writer.writerows([f"{filename or ''}:{liste[0]}"] + liste[1:])


class JSONLDExporter(JSONExporter):
    """
    Exporter to JSON-LD.

    :param filename: Filename where to export. If None, it will print the JSON-LD instead.
    :type filename: str, default None.
    """

    EXT = ".jsonld"
    MODEL_CONTEXT = {
        "fileName": "",  # TODO
        "filePath": "",  # TODO
        "fileFormat": "",  # TODO
        "description": "https://schema.org/description",
    }

    def __init__(self, filename=None):
        if filename:
            super().__init__(filename)
        else:
            self.filename = None

    def __call__(self, model):
        jsonld = {"@context": {}}

        if not model.context:
            raise ValueError("No context found in the given Model.")

        # Add context
        jsonld["@context"].update(model.context)
        jsonld["@context"].update(self.MODEL_CONTEXT)

        def recur(traversal, parent_path=""):
            for path, info in traversal.items():
                if info["descriptiveType"] == NA:
                    if info["traversal"]:
                        yield from (r for r in recur(info["traversal"]))
                else:
                    temp = {}
                    for attr in ATTRS_EXPORT:
                        temp[attr] = info[attr]
                        temp["@type"] = info["descriptiveType"]

                    del temp["descriptiveType"]
                    temp["absolutePath"] = path
                    temp["relativePath"] = path.replace(parent_path, "")

                    if info["traversal"]:
                        temp["contains"] = [r for r in recur(info["traversal"], parent_path=path)]
                    yield temp

        if len(model.traversal) >= 1:
            jsonld["@graph"] = []
            for filename, traversal in model.traversal.items():
                temp = {
                    "@type": "https://schema.org/DigitalDocument",
                    "fileName": filename.split("/")[-1] if filename else None,
                    "filePath": filename if filename else None,
                    "fileFormat": mimetypes.types_map.get(f".{filename.split('.')[-1]}") or None if filename else None,
                    "description": "",
                    "contains": [r for r in recur(traversal)],
                }
                jsonld["@graph"].append(temp)

        if self.filename:
            with open(self.filename, "w") as file:
                json.dump(jsonld, file, indent=2, default=str)
        else:
            print(json.dumps(jsonld, indent=2, default=str))
