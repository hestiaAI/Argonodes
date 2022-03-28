import json
from typing import Optional
from deepdiff import DeepDiff
from helpers import get_json_traversal, get_extended_traversal

FRAME_TEMPLATE = '''
"fieldName": "{fieldname}",
"fieldPath": "{fieldpath}",
"foundType": "{foundtype}",
"descriptiveType": "{descriptivetype}",
"unique": {unique},
"default": "{default}",
"description": "{description}",
"exampleData": [{exampledata}],
"regex": "{regex}",
"contains": {contains}
'''

SAMPLE_TEMPLATE = '''
"fieldName": "{fieldname}",
"contains": {contains}
'''

SAMPLE_TEMPLATE_WITH_PATHS = '''
"fieldName": "{fieldname}",
"fieldPath": "{fieldpath}",
"contains": {contains}
'''


class Model:
    """
    Model for a data frame.
    Internal: Python Dict.
    External: Either JSon or a String.
    """
    def __init__(self, context=None, filenames=None, traversal=None, frame=None, multiple=True):
        if context:
            self.context = context
        else:
            self.context = DEFAULT_CONTEXT

        if filenames:
            self.filenames = filenames
        else:
            self.filenames = []

        if traversal:
            self.traversal = traversal
        else:
            self.traversal = {}

        if frame:
            self.frame = frame
        else:
            self.frame = {}

        self.multiple = multiple

    def add_files(self, filenames) -> int:
        if not isinstance(filenames, list):
            filenames = [filenames]

        for filename in filenames:
            try:
                with open(filename, "r"):  # This is for checking the file exists.
                    self.filenames.append(filename)
            except FileNotFoundError:
                print(f"Warning: {filename} could not be opened.")

        return len(self.filenames)

    def remove_files(self, filenames) -> int:
        if not isinstance(filenames, list):
            filenames = [filenames]

        for filename in filenames:
            try:
                self.filenames.remove(filename)
            except ValueError as e:
                print(f"Warning: {filename} was not found in the list.")

        return len(self.filenames)

    def process_files(self, apply=True) -> list[tuple[str, dict]]:
        if apply:
            full_traversal = self.traversal
        else:
            full_traversal = self.traversal.copy()
        changes = []

        for filename in self.filenames:
            with open(filename, "r") as f:
                json_data = json.load(f)

            traversal = get_json_traversal(json_data)
            changes.append((filename, DeepDiff(traversal, traversal)))
            full_traversal.update(traversal)

        return changes

    def apply_self_traversal(self):
        self.frame = get_extended_traversal(traversal=self.traversal)

    def _frame_and_context(self) -> dict:
        frame_and_context = self.context.copy()
        frame_and_context.update(self.frame)

        return frame_and_context

    def export_model(self, text=True, filename=None) -> Optional[str]:
        if text:
            return json.dumps(self._frame_and_context())
        elif filename:
            with open(filename, "w") as file:
                json.dump(self._frame_and_context(), filename, indent=4)
            return
