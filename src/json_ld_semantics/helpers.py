from typing import Union, Any
import json
from typing import Optional


def get_paths(d, root="$", with_root=True, full=True) -> set:
    def recur(d):
        if isinstance(d, dict):
            for key, value in d.items():
                yield f'.{key}'
                yield from (f'.{key}{p}' for p in recur(value))

        elif isinstance(d, list):
            for i, value in enumerate(d):
                yield f'[*]'
                yield from (f'[*]{p}' for p in recur(value))

    result = set(root + p for p in recur(d))

    if with_root:
        result.add(root)

    if not full:
        result = set(r for r in result if r[-3:] != "[*]")

    return result


def get_json_traversal(data) -> Optional[dict]:
    def treeify(inner_data, root="$") -> Optional[dict]:
        if isinstance(inner_data, dict):
            return {key: (f"{root}.{key}", type(children).__name__, treeify(children, root=f"{root}.{key}")) for
                    key, children in inner_data.items()}
        elif isinstance(inner_data, list):
            return {"*": (f"{root}[*]", type(inner_data).__name__, treeify(children, root=f"{root}[*]")) for children in inner_data}
        else:
            return None

    return treeify(data)


FRAME_TEMPLATE = '''
"fieldName": "{fieldname}",
"fieldPath": "{fieldpath}",
"foundType": {foundtype},
"descriptiveType": "{descriptivetype}",
"unique": {unique},
"default": "{default}",
"description": "{description}",
"exampleData": [{exampledata}],
"regex": "{regex}",
"contains": {contains}
'''


def format_template(template=FRAME_TEMPLATE, **kwargs) -> str:
    """
    Template formatting helper.
    :param template: String template with format placeholders (e.g., `{thing}`).
    :param kwargs: Elements to go in the placeholders.
    :return: Formatted string.
    """
    return template.format(**kwargs).replace("\n", "").replace("False", "false").replace("True", "true").replace("None",
                                                                                                                 "null")


def get_extended_traversal(json_data=None, traversal=None, raw=False) -> Union[str, Any]:
    if not json_data and not traversal:
        raise ValueError("Need aither `json_data` or `traversal`.")

    if json_data:
        traversal = get_json_traversal(json_data)

    def recur(data) -> str:
        tmp = []

        for key, (path, typ, contains) in data.items():
            if typ == "NoneType":
                typ = "null"
            else:
                typ = f"\"{typ}\""

            if key == "*":
                tmp.append("{" + format_template(
                    FRAME_TEMPLATE,
                    fieldname="<unnamed list>",
                    fieldpath=path,
                    foundtype=typ,
                    descriptivetype=None,
                    unique=False,
                    default=None,
                    description=None,
                    exampledata=None,
                    regex=None,
                    contains="[" + recur(contains) + "]",
                ) + "}")
            else:
                if contains:
                    tmp.append("{" + format_template(
                        FRAME_TEMPLATE,
                        fieldname=key,
                        fieldpath=path,
                        foundtype=typ,
                        descriptivetype=None,
                        unique=False,
                        default=None,
                        description=None,
                        exampledata=None,
                        regex=None,
                        contains="[" + recur(contains) + "]",
                    ) + "}")
                else:
                    tmp.append("{" + format_template(
                        FRAME_TEMPLATE,
                        fieldname=key,
                        fieldpath=path,
                        foundtype=typ,
                        descriptivetype=None,
                        unique=False,
                        default=None,
                        description=None,
                        exampledata=None,
                        regex=None,
                        contains="null",
                    ) + "}")

        tmp = ','.join(tmp).replace("\\", "")
        return tmp

    if raw:
        return recur(traversal)
    else:
        return json.loads(recur(traversal))
