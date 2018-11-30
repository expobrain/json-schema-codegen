import ast
import astor
from re import search


class Python3ObjectGenerator(object):
    @staticmethod
    def class_name(s) -> str:
        name = search("^(.*)Schema$", s)
        if name is not None:
            return name.group(1)
        else:
            raise ValueError("Cannot form class name from schema")

    @staticmethod
    def _get_property_name(node_assign):
        name = node_assign.targets[0]
        return name.id

    @staticmethod
    def _nesting_class(node_assign):
        for node in ast.walk(node_assign):
            if isinstance(node, ast.Call):
                if node.func.attr == "Nested":
                    return Python3ObjectGenerator.class_name(node.args[0].id)

    @staticmethod
    def _non_primitive_nested_list(node_assign):
        return (
            node_assign.value.func.attr == "List"
            and node_assign.value.args[0].func.attr == "Nested"
        )

    @staticmethod
    def assign_property(node_assign, object_):
        prop = Python3ObjectGenerator._get_property_name(node_assign)

        if Python3ObjectGenerator._non_primitive_nested_list(node_assign):
            # If the nested list is non-primitive, initialise sub-classes in a list comp
            # If the nest is primitive, we can simply get it
            # Marshmallow will do the type marshalling
            value = ast.ListComp(
                elt=ast.Call(
                    func=ast.Name(id=Python3ObjectGenerator._nesting_class(node_assign)),
                    args=[ast.Name(id="el")],
                    keywords=[],
                ),
                generators=[
                    ast.comprehension(
                        target=ast.Name(id="el"),
                        iter=ast.Call(
                            func=ast.Attribute(value=ast.Name(id=object_), attr="get"),
                            args=[ast.Str(s=prop), ast.Dict(keys=[], values=[])],
                            keywords=[],
                        ),
                        ifs=[],
                        is_async=0,
                    )
                ],
            )

        else:
            # TODO: Add type annotations
            # Assign the property as self.prop = table.get("prop")
            value = ast.Call(
                func=ast.Attribute(value=ast.Name(id=object_), attr="get"),
                args=[ast.Str(s=prop)],
                keywords=[],
            )
            # If the property is required, assign as self.prop = table["prop"]
            for node in ast.walk(node_assign):
                if isinstance(node, ast.keyword):
                    if "required" in node.arg:
                        value = ast.Subscript(
                            value=ast.Name(id=object_), slice=ast.Index(value=ast.Str(s=prop))
                        )

        return ast.Assign(
            targets=[ast.Attribute(value=ast.Name(id="self"), attr=prop)], value=value
        )

    @staticmethod
    def construct_class(schema):
        name = Python3ObjectGenerator.class_name(schema.name)
        name_lower = name.lower()

        # Bundle function arguments and keywords
        fn_arguments = ast.arguments(
            args=[
                ast.arg(arg="self", annotation=None),
                ast.arg(arg=name_lower, annotation=ast.Name(id="dict")),
            ],
            vararg=None,
            kwarg=None,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[ast.NameConstant(value=None)],
        )

        # Generate class constructor
        fn_init = ast.FunctionDef(
            name="__init__",
            args=fn_arguments,
            body=[
                Python3ObjectGenerator.assign_property(node, name_lower)
                for node in schema.body
                if isinstance(node, ast.Assign)
            ],
            decorator_list=[],
            returns=None,
        )

        return ast.ClassDef(
            name=name,
            bases=[ast.Name(id="object")],
            body=[fn_init],
            decorator_list=[],
            keywords=[],
        )

    @staticmethod
    def construct_class_post_load_helper(schema):
        name = Python3ObjectGenerator.class_name(schema.name)
        name_lower = name.lower()

        fn_args = ast.arguments(
            args=[ast.arg(arg="self", annotation=None), ast.arg(arg="table", annotation=None)],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )

        fn_body = ast.Return(
            value=ast.Call(func=ast.Name(id=name), args=[ast.Name(id=name_lower)], keywords=[])
        )

        return ast.FunctionDef(
            name="make_" + name_lower,
            args=fn_args,
            body=[fn_body],
            decorator_list=[ast.Name(id="post_load")],
            returns=None,
        )

