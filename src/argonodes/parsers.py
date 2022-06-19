"""
Parsers are tools for converting data sources into a JSON format, usable by Argonodes.

There are different Parsers depending on the original source. Basically, Parsers should implement the dunder ``__call__``, that takes into account a parameter ``data_in``, which corresponds to, well, the data to parse. That data may be either a string, or a File object.

Basic usage: ``parser = Parser(); json_data = parser(data)``
"""
from abc import ABC, abstractmethod
from io import StringIO
from typing import Union
import csv
import io
import json


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
    def __call__(self, data_in) -> Union[dict, list]:
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

        data_in[0] = "["  # Quick and dirty!

        return json.loads("\n".join(data_in))


class ZIPParser:
    def __init__(self, parser=None, verbose=False):
        self.parser = parser()
        self.verbose = verbose

    def __call__(self, filename, verbose=False):
        import zipfile

        trees = []

        try:
            with zipfile.ZipFile(filename, mode="r") as archive:
                for filename in archive.namelist():
                    try:
                        content = archive.read(filename).decode(encoding="utf-8")
                        if self.parser:
                            json_data = self.parser(content)
                        else:
                            json_data = json.loads(content)

                        trees.append(Tree(json_data, filename=filename))
                        if verbose or self.verbose:
                            print(f"- {filename} added to the list.")
                    except:
                        continue

            return trees

        except zipfile.BadZipFile as error:
            raise error
