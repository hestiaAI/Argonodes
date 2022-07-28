"""
Parsers are tools for converting data sources into a JSON format, usable by Argonodes.

There are different Parsers depending on the original source. Basically, Parsers should implement the dunder ``__call__``, that takes into account a parameter ``data_in``, which corresponds to, well, the data to parse. That data may be either a string, or a File object.

Basic usage: ``parser = Parser(); json_data = parser(data)``
"""
from abc import ABC, abstractmethod
from io import StringIO
from json import JSONDecodeError
from typing import Union
import csv
import json
import os.path
import re


from .nodes import Tree


class Parser(ABC):
    """
    Abstraction for every Parser.
    """

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def __call__(self, data_in):
        if isinstance(data_in, str):
            pass
        else:
            pass


class JSONParser(Parser):
    """
    A default parser that will take JSON and produce JSON.

    :param data_in: The data source.
    :type data_in: str or File.
    """

    def __call__(self, data_in):
        if isinstance(data_in, str):
            try:
                return json.loads(data_in)
            except ValueError:
                raise ValueError("This is not a correct JSON string.")
        else:
            try:
                return json.load(data_in)
            except ValueError:
                raise ValueError("This is not a correct JSON file.")


class CSVParser(Parser):
    """
    CSV to JSON.

    :param data_in: The data source.
    :type data_in: str or File.
    """

    def __call__(self, data_in, *args, **kwargs) -> list:
        if isinstance(data_in, str):
            data_in = StringIO(data_in)

        if not kwargs:
            dialect = csv.Sniffer().sniff(data_in.read(1024))
            data_in.seek(0)
            reader = csv.DictReader(data_in, dialect=dialect)
        else:
            reader = csv.DictReader(data_in, **kwargs)

        return [dict(row) for row in reader]


class XMLParser(Parser):
    """
    XML to JSON.

    Warning, it uses an external package that you should install first: `pip install xmltodict`.

    :param data_in: The data source.
    :type data_in: str or File.
    """

    def __call__(self, data_in, *args, **kwargs):
        import xmltodict

        if not isinstance(data_in, str):
            data_in = data_in.read()

        return json.dumps(xmltodict.parse(data_in))


class JSParser(Parser):
    pass


class TwitterJSParser(JSParser):
    """ """

    def __call__(self, data_in):
        if not isinstance(data_in, str):
            data_in = data_in.read().split("\n")
        else:
            data_in = data_in.split("\n")

        if data_in:
            if "[" in data_in[0]:
                data_in[0] = "["
                if len(data_in) == 1:
                    data_in[0] += "]"
            elif "{" in data_in[0]:
                data_in[0] = "{"
                if len(data_in) == 1:
                    data_in[0] += "}"
            else:
                raise AttributeError("Not JSON compatible.")

        return json.loads("\n".join(data_in))


class ZIPParser:
    """ """

    def __init__(self, parser=None, regex=None, extension=None, mime=None, verbose=None):
        self.parser = parser()
        self.regex = regex
        self.extension = f".{extension}" if extension[0] != "." else extension
        self.mime = mime
        self.verbose = verbose or 0

    def __call__(self, filename):
        import zipfile

        trees = {}

        try:
            with zipfile.ZipFile(filename, mode="r") as archive:
                total_files = len(archive.namelist())
                for filename in archive.namelist():
                    try:
                        if self.regex and not re.match(self.regex, filename):
                            raise AssertionError("Regex not matching.")

                        _, ext = os.path.splitext(filename)
                        if self.extension and ext != self.extension:
                            raise AssertionError("Wrong extension.")

                        if self.mime and False:
                            raise AssertionError("Wrong MIME type.")

                        content = archive.read(filename).decode(encoding="utf-8")

                        if self.parser:
                            json_data = self.parser(content)
                        else:
                            json_data = json.loads(content)

                        trees[filename] = Tree(json_data, filename=filename)
                        if self.verbose > 1:
                            print(f"- ✅ {filename} added to the list.")
                    except AssertionError as e:
                        if self.verbose > 1:
                            print(f"- ❌ {filename} NOT added to the list (AssertionError: {e}).")
                        continue
                    except JSONDecodeError as e:
                        if self.verbose > 0:
                            print(
                                f"- ❌ {filename} NOT added to the list (JSONDecodeError: {e}). ❗️ You may want to check the content of the file!"
                            )
                        continue

            trees = dict(sorted(trees.items()))

            if self.verbose > 0:
                print(f"=> {len(trees)} Trees created from {total_files} folders and files:")
                print("\n".join([f"- {filename}" for filename in trees.keys()]))

            return trees

        except zipfile.BadZipFile as error:
            raise error


MIME_TO_PARSER = {
    "text/csv": CSVParser,
    "application/json": JSONParser,
    "application/javascript": TwitterJSParser,
    "application/x-javascript": TwitterJSParser,
    "application/x-rar-compressed": None,
    "application/zip": ZIPParser,
    "application/x-zip-compressed": ZIPParser,
    "multipart/x-zip": ZIPParser,
}
