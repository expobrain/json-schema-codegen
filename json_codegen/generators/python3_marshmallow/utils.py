import ast
from re import search
from typing import List

marshmallow_type_map = {
    "integer": "Integer",
    "string": "String",
    "boolean": "Boolean",
    "array": "List",
    "number": "Number",
    "object": "Dict",
}

python_type_map = {
    "Integer": "int",
    "String": "str",
    "Boolean": "bool",
    "List": "List",
    "Number": "float",
    "Dict": "dict",
}


def upper_first_letter(s):
    """
    Assumes custom types of two words are defined as customType
    such that the class name is CustomTypeSchema
    """
    return s[0].upper() + s[1:]


def class_name(s, strict=True) -> str:
    name = search("^(.*)Schema$", s)
    if name is not None:
        return name.group(1)
    else:
        if strict:
            raise ValueError("Cannot form class name from schema")
        else:
            return None


class Annotations:
    def __init__(self, node):
        self.node: List[ast.stmt] = node
        self.nested_type: bool = self._is_nested_type()
        self.type: str = self.type_annotation()

    def type_annotation(self):
        """
        Gets the type hint for a marshmallow field
        """
        # If the keyword required has been supplied, wrap the type hint
        # in `Optional`. As the class is generated, `required=False` does
        # not occur
        for node in ast.walk(self.node):
            if isinstance(node, ast.keyword) and node.arg in ["required", "default"]:
                optional = False
                break
        else:
            optional = True

        for node in ast.walk(self.node):
            if isinstance(node, ast.Attribute) and node.value.id == "fields_":
                # If the type is not a `List`, return either the type (primitive or custom)
                type_ = python_type_map.get(node.attr, upper_first_letter(node.attr))

                if type_ != "List":
                    return self.annotation(type_, list_=False, optional=optional)
                elif self.nested_type is not None:
                    return self.annotation([self.nested_type], list_=True, optional=optional)
                else:
                    return self.annotation(["Any"], list_=True, optional=optional)

            if isinstance(node, ast.Call) and node.func.attr == "Nested":
                # If the type is a List, wrap the subtype with `List`
                subtype = [class_name(n.id) for n in node.args]

                if len(subtype) != 1:
                    raise ValueError("Nested Schema called with more than 1 type")

                return self.annotation(subtype, list_=True, optional=optional)

        else:
            raise NotImplementedError("Unexpected node type")

    def _is_nested_type(self):
        for node in ast.walk(self.node):
            if isinstance(node, ast.Call) and node.func.attr == "Nested" and len(node.args) > 0:
                return class_name(node.args[0].id)

    def _annotation_optional(self, type_, optional=False):
        if optional:
            return ast.Subscript(
                value=ast.Name(id="Optional"), slice=ast.Index(value=ast.Name(id=type_))
            )
        else:
            return ast.Name(id=type_)

    def _annotation_list(self, type_):
        return ast.Subscript(
            value=ast.Name(id="List"), slice=ast.Index(value=ast.Name(id=type_[0]))
        )

    def annotation(self, type_, list_, optional):
        if list_:
            type_ = self._annotation_list(type_)
        if optional:
            type_ = self._annotation_optional(type_, optional)

        if not (list_ or optional):
            return ast.Name(id=type_)
        else:
            return type_
