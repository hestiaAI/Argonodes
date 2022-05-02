# https://wang-yimu.com/the-visitor-pattern/

from abc import ABC, abstractmethod


PROTECTED_ATTRS = ["fieldName", "data", "foundType", "parent", "children", "path"]


class Protected(type):
    """Protection for changing source data in semantics."""

    def __setattr__(cls, key, value):
        if key in PROTECTED_ATTRS:
            raise AttributeError(f"Cannot modify `{key}`.")
        else:
            return type.__setattr__(cls, key, value)

    def __delattr__(cls, key):
        if key in PROTECTED_ATTRS:
            raise AttributeError(f"Cannot delete `{key}`.")
        else:
            return type.__delattr__(cls, key)


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
