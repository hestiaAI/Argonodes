from pyld import jsonld
import json
from model import Model


class Semantics:
    def __init__(self, data=None, model=None):
        if data:
            self.data = [data]
        else:
            self.data = []

        if self.model:
            self.model = model
        else:
            self.model = Model()
