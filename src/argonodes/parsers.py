"""
Parsers are tools for converting data sources into a JSON format, usable by Argonodes.

There are different Parsers depending on the original source. Basically, Parsers should implement the dunder `__call__`, that takes into account a parameter `data_in`, which corresponds to, well, the data to parse. That data may be either a string, or a File object.
"""
from abc import ABC, abstractmethod
from typing import Union
import csv


class Parser(ABC):
    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def __call__(self, data_in, *args, **kwargs) -> Union[dict, list]:
        pass


class InferParser(Parser):
    pass


class CSVParser(Parser):
    def __call__(self, data_in, *args, **kwargs) -> list:
        if not kwargs:
            dialect = csv.Sniffer().sniff(data_in.read(1024))
            data_in.seek(0)
            reader = csv.DictReader(data_in, dialect=dialect)
        else:
            reader = csv.DictReader(data_in, **kwargs)

        return [dict(row) for row in reader]


class SGMLParser(Parser):
    pass


class XMLParser(SGMLParser):
    pass


class HTMLParser(SGMLParser):
    pass
