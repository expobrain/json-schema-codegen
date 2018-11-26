from __future__ import unicode_literals, print_function, division
from typing import List


class Table(object):
    def __init__(self, data=None):
        data = data or {}
        self.access: List[str] = [0] if data.get("access") is None else data.get("access")
        self.description = data.get("description")
        self.disabled = False if data.get("disabled") is None else data.get("disabled")
        self.fields = data.get("fields")
        self.name = data.get("name")
        self.source = data.get("source")
        self.transforms = data.get("transforms")


import astor
import ast


# def from_dict(d: dict):
#     out = Transform()
#     if not d:
#         return out
#     if "name" not in d:
#         raise Exception("Missing mandatory field mandatory str Transform->name in Transform")
#     out.name = d.get("name", "")
#     out.params = d.get("params")
#     return out


class Fn_DictFrom(object):
    def __init__(self):
        self.name = "from_dict"
        self.body = []

    def fn_args(self):
        return ast.arguments(
            args=[ast.arg(arg="d", annotation="dict")], vararg=None, kwarg=None, defaults=[]
        )

    def fn_body(self):
        return ast.Assign(targets=[ast.Name(id="data")], value=ast.Dict(keys=[], values=[]))

    def fn_function(self):
        return ast.FunctionDef(
            name=self.name,
            args=self.fn_args(),
            body=[self.fn_body()],
            returns=None,
            decorator_list=[],
        )

    def print(self):
        self.body.append(self.fn_function())
        print(astor.to_source(ast.Module(body=self.body)))


Fn_DictFrom().print()
