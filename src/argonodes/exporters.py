"""
Exporters are useful to export Models in multiple formats.

In some cases, it may be necessary to export in formats that do not correspond to the basic Argonodes format (e.g., CSV, SQL, ...). It is therefore possible to build custom exporters that meet these needs.

Basic usage: ``exporter = Exporter(); model.export(exporter)``
"""
from abc import ABC, abstractmethod
import csv
import io
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

    def __init__(self, file_or_buf=None):
        self.filename = None
        self.buf = None

        if file_or_buf:
            if isinstance(file_or_buf, str):
                _, ext = os.path.splitext(file_or_buf)
                if ext != self.EXT:
                    file_or_buf += self.EXT
                    print(
                        f"Warning: {self.EXT} will automatically be added at the end of the file name.\nResult will thus be {file_or_buf}."
                    )
                self.filename = file_or_buf
            elif isinstance(file_or_buf, io.IOBase):
                self.buf = file_or_buf
            else:
                print(f"Not supported: {type(file_or_buf)}.")

    @abstractmethod
    def __call__(self, model):
        if self.filename:
            with open(self.filename):
                raise NotImplementedError
        elif self.buf:
            raise NotImplementedError
        else:
            raise NotImplementedError


class PickleExporter(Exporter):
    """
    Exporter to a Python Pickle.

    :param file_or_buf: File or buffer where to export.
    :type file_or_buf: str or io.BytesIO
    """

    EXT = ".pickle"

    def __init__(self, file_or_buf):
        super().__init__(file_or_buf)

    def __call__(self, model):
        if self.filename:
            with open(self.filename, "wb") as file:
                pickle.dump(model.traversal, file)
        elif self.buf:
            if isinstance(self.buf, io.BytesIO):
                pickle.dump(model.traversal, self.buf)
            else:
                raise AttributeError
        else:
            raise NotImplementedError


class JSONExporter(Exporter):
    """
    Exporter to JSON.

    :param file_or_buf: File or buffer where to export. If None, it will print the JSON instead.
    :type file_or_buf: str or io.StringIO, default None.
    """

    EXT = ".json"

    def __init__(self, file_or_buf=None):
        super().__init__(file_or_buf)

    def __call__(self, model):
        if self.filename:
            with open(self.filename, "w") as file:
                json.dump(model.traversal, file, indent=2, default=str)
        elif self.buf:
            if isinstance(self.buf, io.StringIO):
                json.dump(model.traversal, self.buf, indent=2, default=str)
            else:
                raise AttributeError
        else:
            print(json.dumps(model.traversal, indent=2, default=str))


class MarkdownExporter(Exporter):
    """
    Exporter to Markdown.

    :param file_or_buf: File or buffer where to export. If None, it will print the JSON instead.
    :type file_or_buf: str or io.StringIO, default None.
    """

    EXT = ".md"

    def __init__(self, file_or_buf=None):
        super().__init__(file_or_buf)

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
        elif self.buf:
            if isinstance(self.buf, io.StringIO):
                for m in markdown:
                    self.buf.write(f"{m}\n")
            else:
                raise AttributeError
        else:
            print("\n".join(markdown))


class CSVExporter(Exporter):
    """
    Exporter to a CSV.

    :param file: Filename where to export.
    :type file: str
    """

    EXT = ".csv"

    def __init__(self, file):
        super().__init__(file)

    def __call__(self, model):
        headers, listes = model.to_list()

        if self.filename:
            with open(self.filename, "w") as csvfile:
                writer = csv.writer(csvfile)

                writer.writerow(headers)
                for file, liste in listes.items():
                    for l in liste:
                        writer.writerows([f"{file or ''}:{l[0]}"] + l[1:])
        elif self.buf:
            self.buf.write(headers)
            for file, liste in listes.items():
                for l in liste:
                    self.buf.write([f"{file or ''}:{l[0]}"] + l[1:])
        else:
            print(headers)
            for file, liste in listes.items():
                for l in liste:
                    print([f"{file or ''}:{l[0]}"] + l[1:])


class JSONLDExporter(JSONExporter):
    """
    Exporter to JSON-LD.

    :param file: Filename where to export. If None, it will print the JSON-LD instead.
    :type file: str, default None.
    """

    EXT = ".jsonld"
    MODEL_CONTEXT = {
        "fileName": "https://schema.org/name",
        "filePath": "https://www.wikidata.org/wiki/Q817765",
        "fileFormat": "https://schema.org/fileFormat",
        "description": "https://schema.org/description",
    }

    def __init__(self, file_or_buf=None):
        super().__init__(file_or_buf)

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
                    # TODO This is just dirty
                    temp["fieldName"] = path.split(".")[-1]
                    # End dirty

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
                    "description": model.description,
                    "contains": [r for r in recur(traversal)],
                }
                jsonld["@graph"].append(temp)

        if self.filename:
            with open(self.filename, "w") as file:
                json.dump(jsonld, file, indent=2, default=str)
        elif self.buf:
            if isinstance(self.buf, io.StringIO):
                json.dump(jsonld, self.buf, indent=2, default=str)
            else:
                raise AttributeError
        else:
            print(json.dumps(jsonld, indent=2, default=str))
