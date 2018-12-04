import ast
import astor
from re import search
from . import python_type_map


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
    def _annotation_optional(type_, optional=False):
        if optional:
            return ast.Subscript(
                value=ast.Name(id="Optional"), slice=ast.Index(value=ast.Name(id=type_))
            )
        else:
            return ast.Name(id=type_)

    @staticmethod
    def _annotation_list(subtype):
        return "List[" + subtype[0] + "]"

    @staticmethod
    def _type_annotation(node_assign):
        """
        Gets the type hint for a marshmallow field
        """
        # If the keyword required has been supplied, wrap the type hint
        # in `Optional`. As the class is generated, `required=False` does
        # not occur
        optional = True
        for node in ast.walk(node_assign):
            if isinstance(node, ast.keyword) and node.arg == "required":
                optional = False

        for node in ast.walk(node_assign):

            if isinstance(node, ast.Attribute) and node.value.id == "fields_":
                # If the type is not a `List`, return either the type (primitive or custom)
                type_annotation = python_type_map.get(
                    node.attr, Python3ObjectGenerator.upper_first_letter(node.attr)
                )
                if type_annotation != "List":
                    return Python3ObjectGenerator._annotation_optional(type_annotation, optional)

            if isinstance(node, ast.Call) and node.func.attr == "Nested":
                # If the type is a List, wrap the subtype with `List`
                subtype = [Python3ObjectGenerator.class_name(n.id) for n in node.args]
                if len(subtype) != 1:
                    raise ValueError("Nested Schema called with more than 1 type")
                return Python3ObjectGenerator._annotation_optional(
                    Python3ObjectGenerator._annotation_list(subtype), optional
                )

    @staticmethod
    def assign_property(node_assign, object_):
        """
        Required property         -> self.prop  = parent_dict["prop"]
        Optional property         -> self.prop  = parent_dict.get("prop")
        Primative nested list     -> self.prop  = parent_dict.get("prop") 
        Non-primative nested list -> self.props = [PropertyClass(el) for el in parent_dict.get('props', {})]
        """
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

        return ast.AnnAssign(
            target=ast.Attribute(value=ast.Name(id="self"), attr=prop),
            value=value,
            simple=0,
            # annotation=ast.Name(id=Python3ObjectGenerator._type_annotation(node_assign)),
            annotation=Python3ObjectGenerator._type_annotation(node_assign),
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
            defaults=[],
        )

        fn_body = [
            Python3ObjectGenerator.assign_property(node, name_lower)
            for node in schema.body
            if isinstance(node, ast.Assign)
        ]

        # pass if no Assign nodes
        if len(fn_body) == 0:
            fn_body = [ast.Pass()]

        # Generate class constructor
        class_body = [
            ast.FunctionDef(
                name="__init__", args=fn_arguments, body=fn_body, decorator_list=[], returns=None
            ),
            Python3ObjectGenerator._construct_to_("json")(schema),
            Python3ObjectGenerator._construct_to_("dict")(schema),
            Python3ObjectGenerator.construct_from_json(schema),
        ]

        return ast.ClassDef(
            name=name,
            bases=[ast.Name(id="object")],
            body=class_body,
            decorator_list=[],
            keywords=[],
        )

    @staticmethod
    def _construct_to_(output):

        if output == "json":
            method = "dumps"
        elif output == "dict":
            method = "dump"
        else:
            raise NotImplementedError("Only deserialisation to json or dict supported")

        def _construct_to_helper(schema):

            fn_args = ast.arguments(
                args=[ast.arg(arg="self", annotation=None)],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            )

            fn_body = [
                ast.Return(
                    value=ast.Attribute(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Call(
                                    func=ast.Name(id=schema.name),
                                    args=[],
                                    keywords=[
                                        ast.keyword(
                                            arg="strict", value=ast.NameConstant(value=True)
                                        )
                                    ],
                                ),
                                attr=method,
                            ),
                            args=[ast.Name(id="self")],
                            keywords=[],
                        ),
                        attr="data",
                    )
                )
            ]

            return ast.FunctionDef(
                name=f"to_{output}", args=fn_args, body=fn_body, decorator_list=[], returns=None
            )

        return _construct_to_helper

    @staticmethod
    def construct_from_json(schema):

        fn_args = ast.arguments(
            args=[
                ast.arg(arg="json", annotation=ast.Name(id="str")),
                ast.arg(arg="only", annotation=None),
            ],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[ast.NameConstant(value=None)],
        )

        fn_body = [
            ast.Return(
                ast.Attribute(
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Call(
                                func=ast.Name(id=schema.name),
                                args=[],
                                keywords=[
                                    ast.keyword(arg="strict", value=ast.NameConstant(value=True)),
                                    ast.keyword(arg="only", value=ast.Name(id="only")),
                                ],
                            ),
                            attr="loads",
                        ),
                        args=[ast.Name(id="json")],
                        keywords=[],
                    ),
                    attr="data",
                )
            )
        ]

        return ast.FunctionDef(
            name="from_json",
            args=fn_args,
            body=fn_body,
            decorator_list=[ast.Name(id="staticmethod")],
            returns=None,
        )

    @staticmethod
    def upper_first_letter(s):
        """
        Assumes custom types of two words are defined as customType
        such that the class name is CustomTypeSchema
        """
        return s[0].upper() + s[1:]

