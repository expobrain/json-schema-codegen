import astor
import ast


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
        body.append(ast.Assign(targets=[ast.Name(id="d")], value=ast.Dict(keys=[], values=[])))
        body.append(self._return_early_if_no_obj(check="d", ret="out"))

        for required in self.required:
            body.append(self._if_missing_required(required))

        body.append(self._append_keys_to_out_obj(body))
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

    def _append_keys_to_out_obj(self, body):
        body.append(
            ast.For(
                target=ast.Name(id="k"),
                iter=ast.Call(
                    func=ast.Attribute(value=ast.Name(id="d"), attr="keys"), args=[], keywords=[]
                ),
                body=[
                    ast.Assign(
                        targets=[
                            ast.Subscript(
                                value=ast.Name(id="out"), slice=ast.Index(value=ast.Name(id="k"))
                            )
                        ],
                        value=ast.Call(
                            func=ast.Attribute(value=ast.Name(id="d"), attr="get"),
                            args=[ast.Name(id="k")],
                            keywords=[],
                        ),
                    )
                ],
                orelse=[],
            )
        )

    def _return_early_if_no_obj(self, check, ret):
        ast.If(
            test=ast.UnaryOp(op=ast.Not(), operand=ast.Name(id=check)),
            body=[ast.Return(value=ast.Name(id=ret))],
            orelse=[],
        )

    def print(self):
        print(astor.to_source(ast.Module(body=self.built_fn)))


Fn_DictFrom().print()
