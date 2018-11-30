import ast
import astor
from re import search

from ast import *

class_def = ClassDef(
    name="TableSchema",
    bases=[Name(id="Schema")],
    keywords=[],
    body=[
        Assign(
            targets=[Name(id="access")],
            value=Call(
                func=Attribute(value=Name(id="fields_"), attr="List"),
                args=[
                    Call(
                        func=Attribute(value=Name(id="fields_"), attr="String"),
                        args=[],
                        keywords=[],
                    )
                ],
                keywords=[keyword(arg="default", value=List(elts=[Num(n=0)]))],
            ),
        ),
        Assign(
            targets=[Name(id="description")],
            value=Call(
                func=Attribute(value=Name(id="fields_"), attr="String"), args=[], keywords=[]
            ),
        ),
        Assign(
            targets=[Name(id="disabled")],
            value=Call(
                func=Attribute(value=Name(id="fields_"), attr="Boolean"),
                args=[],
                keywords=[keyword(arg="default", value=NameConstant(value=False))],
            ),
        ),
        Assign(
            targets=[Name(id="fields")],
            value=Call(
                func=Attribute(value=Name(id="fields_"), attr="List"),
                args=[
                    Call(
                        func=Attribute(value=Name(id="fields_"), attr="Nested"),
                        args=[Name(id="FieldSchema")],
                        keywords=[],
                    )
                ],
                keywords=[],
            ),
        ),
        Assign(
            targets=[Name(id="name")],
            value=Call(
                func=Attribute(value=Name(id="fields_"), attr="String"),
                args=[],
                keywords=[keyword(arg="required", value=NameConstant(value=True))],
            ),
        ),
        Assign(
            targets=[Name(id="source")],
            value=Call(
                func=Attribute(value=Name(id="fields_"), attr="String"),
                args=[],
                keywords=[keyword(arg="required", value=NameConstant(value=True))],
            ),
        ),
        Assign(
            targets=[Name(id="transforms")],
            value=Call(
                func=Attribute(value=Name(id="fields_"), attr="List"),
                args=[
                    Call(
                        func=Attribute(value=Name(id="fields_"), attr="Nested"),
                        args=[Name(id="TransformSchema")],
                        keywords=[],
                    )
                ],
                keywords=[],
            ),
        ),
    ],
    decorator_list=[],
)

assign = class_def.body[0]


def hi(ass):
    ass
    pass


hi(assign)


class Python3ObjectGenerator(object):
    @staticmethod
    def object_name(s) -> str:
        name = search("^(.*)Schema$", s)
        if name is not None:
            return name.group(1)
        else:
            raise ValueError("Cannot form object name from schema")

    @staticmethod
    def _get_property_name(node_assign):
        name = node_assign.targets[0]
        return name.id

    @staticmethod
    def _nesting_class(node_assign):
        for node in walk(node_assign):
            if isinstance(node, ast.Call):
                if node.func.attr == "Nested":
                    return Python3ObjectGenerator.object_name(node.args[0].id)

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
            value = ListComp(
                elt=Call(
                    func=Name(id=Python3ObjectGenerator._nesting_class(node_assign)),
                    args=[Name(id="el")],
                    keywords=[],
                ),
                generators=[
                    comprehension(
                        target=Name(id="el"),
                        iter=Call(
                            func=Attribute(value=Name(id=object_), attr="get"),
                            args=[Str(s=prop)],
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
    def construct_object(schema):
        name = Python3ObjectGenerator.object_name(schema.name)
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
                Python3ObjectGenerator.assign_property(node, name_lower) for node in schema.body
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
