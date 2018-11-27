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
        self.params = {"d": "dict"}
        self.required = ["name", "type"]
        self.built_fn_args = self._get_args()
        self.built_fn_body = self._get_body()
        self.built_fn = self._get_function()

    def _get_args(self):
        params = [ast.arg(arg=k, annotation=v) for (k, v) in self.params.items()]
        args = ast.arguments(args=params, vararg=None, kwarg=None, defaults=[])
        return args

    def _get_body(self):
        body = []
        # out = Transform()
        body.append(ast.Assign(targets=[ast.Name(id="d")], value=ast.Dict(keys=[], values=[])))
        # if not d:
        #    return out
        body.append(
            ast.If(
                test=ast.UnaryOp(op=ast.Not(), operand=ast.Name(id="d")),
                body=[ast.Return(value=ast.Name(id="out"))],
                orelse=[],
            )
        )
        # if {required} not in d:
        #     raise Exception("Required field {required} missing from class")
        for required in self.required:
            body.append(self._if_missing_required(required))

        body.append(ast.Return(ast.Name(id="out")))

        return body

    def _get_function(self):
        return [
            ast.FunctionDef(
                name=self.name,
                args=self.built_fn_args,
                body=self.built_fn_body,
                returns=None,
                decorator_list=[],
            )
        ]

    def _if_missing_required(self, required):
        str_exception = f"Required field {required} missing from Class"
        exception = ast.Call(
            func=ast.Name(id="Exception"), args=[ast.Str(s=str_exception)], keywords=[]
        )
        test = ast.Compare(
            left=ast.Str(s=required), ops=[ast.NotIn()], comparators=[ast.Name(id="d")]
        )
        return ast.If(test=test, body=[ast.Raise(exc=exception, cause=None)], orelse=[])

    def print(self):
        print(astor.to_source(ast.Module(body=self.built_fn)))


Fn_DictFrom().print()
