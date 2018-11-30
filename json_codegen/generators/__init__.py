from .python import Python2Generator
from .javascript_flow import JavaScriptFlowGenerator
from .flow import FlowGenerator


def upper_first_letter(s):
    """
    Assumes custom types of two words are defined as customType
    such that the class name is CustomTypeSchema
    """
    return s[0].upper() + s[1:]


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

from marshmallow import Schema, fields


class B(Schema):
    nest_prop = fields.Integer()


class A(Schema):
    my_prop = fields.Dict(B)


A().load({"my_prop": {"nest_prop": 3}})

