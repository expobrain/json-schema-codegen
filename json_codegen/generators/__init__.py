from .python import Python2Generator
from .javascript_flow import JavaScriptFlowGenerator
from .flow import FlowGenerator


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

