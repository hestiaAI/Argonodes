# https://wang-yimu.com/the-visitor-pattern/

from abc import ABC, abstractmethod


class Traversable(ABC):
    @abstractmethod
    def traverse(self):
        pass


class VisitorBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def on_leaf(self, name, obj):
        pass

    @abstractmethod
    def on_enter_level(self, name):
        pass

    @abstractmethod
    def on_leave_level(self):
        pass

    @abstractmethod
    def on_enter_list(self, name, obj):
        pass

    @abstractmethod
    def on_leave_list(self):
        pass

    def visit(self, name, obj):
        if isinstance(obj, list):
            self.on_enter_list(name, obj)
            for e in obj:
                self.visit(name=None, obj=e)
            self.on_leave_list()
        elif isinstance(obj, Traversable):
            self.on_enter_level(name)
            obj.traverse()
            self.on_leave_level()
        else:
            self.on_leaf(name, obj)
