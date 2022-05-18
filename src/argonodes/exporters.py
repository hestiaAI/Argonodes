"""
Exporters are useful to export Models and Nodes in multiple formats.

In some cases, it may be necessary to export in formats that do not correspond to the basic Argonodes format (e.g., CSV, SQL, ...). It is therefore possible to build custom exporters that meet these needs.

Basic usage: ``exporter = Exporter(); model.export(exporter)``
"""
