import ast

from json_codegen.generators.python3_marshmallow.utils import Annotations, class_name


class ObjectGenerator(object):
    @staticmethod
    def _get_property_name(node_assign):
        name = node_assign.targets[0]
        return name.id

    @staticmethod
    def _nesting_class(node_assign):
        for node in ast.walk(node_assign):
            if isinstance(node, ast.Call):
                if node.func.attr == "Nested":
                    return class_name(node.args[0].id)

    @staticmethod
    def _non_primitive_nested_list(node_assign):
        if node_assign.value.func.attr == "List":
            return (
                len(node_assign.value.args) > 0 and node_assign.value.args[0].func.attr == "Nested"
            )
        else:
            return False

    @staticmethod
    def _init_non_primitive_nested_class(node_assign, object_, prop):
        """
        If the nested list is non-primitive, initialise sub-classes in a list comp
        If the nest is primitive, we can simply get it
        Marshmallow will do the type marshalling
        """
        return ast.ListComp(
            elt=ast.Call(
                func=ast.Name(id=ObjectGenerator._nesting_class(node_assign)),
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

    @staticmethod
    def _get_key_from_object(object_, prop):
        return ast.Call(
            func=ast.Attribute(value=ast.Name(id=object_), attr="get"),
            args=[ast.Str(s=prop)],
            keywords=[],
        )

    @staticmethod
    def _hint_required_property(node_assign, value, object_, prop):
        for node in ast.walk(node_assign):
            if isinstance(node, ast.keyword):
                if "required" in node.arg:
                    value = ast.Subscript(
                        value=ast.Name(id=object_), slice=ast.Index(value=ast.Str(s=prop))
                    )
        return value

    @staticmethod
    def _get_default_for_property(node_assign, value, object_, prop):

        for node in ast.walk(node_assign):
            if isinstance(node, ast.keyword) and node.arg == "required":
                return value

        for node in ast.walk(node_assign):
            if isinstance(node, ast.keyword) and node.arg == "default":
                default_value = [
                    keyword.value
                    for keyword in node_assign.value.keywords
                    if keyword.arg == "default"
                ][0]
                value.args.append(default_value)
                return value
        else:
            return value

    @staticmethod
    def assign_property(node_assign, object_):
        """
        Required property         -> self.prop  = parent_dict["prop"]
        Optional property         -> self.prop  = parent_dict.get("prop")
        Primative nested list     -> self.prop  = parent_dict.get("prop")
        Non-primative nested list -> self.props = [PropertyClass(el) for el in parent_dict.get('props', {})]
        """
        prop = ObjectGenerator._get_property_name(node_assign)

        if ObjectGenerator._non_primitive_nested_list(node_assign):
            value = ObjectGenerator._init_non_primitive_nested_class(node_assign, object_, prop)
        else:
            # Assign the property as self.prop = table.get("prop")
            value = ObjectGenerator._get_key_from_object(object_, prop)

            # If the property is required, assign as self.prop = table["prop"]
            value = ObjectGenerator._hint_required_property(node_assign, value, object_, prop)

            value = ObjectGenerator._get_default_for_property(node_assign, value, object_, prop)

        return ast.AnnAssign(
            target=ast.Attribute(value=ast.Name(id="self"), attr=prop),
            value=value,
            simple=0,
            annotation=Annotations(node_assign).type,
        )

    @staticmethod
    def construct_class(schema):
        name = class_name(schema.name)
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
            ObjectGenerator.assign_property(node, name_lower)
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
            ObjectGenerator._construct_to_("json")(schema),
            ObjectGenerator._construct_to_("dict")(schema),
            ObjectGenerator.construct_from_json(schema),
        ]

        return ast.ClassDef(name=name, bases=[], body=class_body, decorator_list=[], keywords=[])

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
                    value=ast.Call(
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
