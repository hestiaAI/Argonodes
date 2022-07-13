"""
Exporters are useful to export Models and Nodes in multiple formats.

In some cases, it may be necessary to export in formats that do not correspond to the basic Argonodes format (e.g., CSV, SQL, ...). It is therefore possible to build custom exporters that meet these needs.

Basic usage: ``exporter = Exporter(); model.export(exporter)``
"""


class JSONLDExporter:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass
