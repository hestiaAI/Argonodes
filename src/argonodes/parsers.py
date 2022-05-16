from abc import ABC, abstractmethod
from typing import Union
import csv
import json


class Parser(ABC):
    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def __call__(self, data_in) -> Union[dict, list]:
        pass


class JSONParser(Parser):
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
