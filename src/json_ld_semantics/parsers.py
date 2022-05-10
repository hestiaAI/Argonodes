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
