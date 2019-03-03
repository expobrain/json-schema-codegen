import astor

from json_codegen.astlib import python as ast
from json_codegen.core import SchemaParser, BaseGenerator
from json_codegen.types import PropertyType


class Python2Generator(SchemaParser, BaseGenerator):
    def generate(self):
        # Add module imports
        self._body = []

        self._body.extend(self.module_imports())

        # Generates definitions first
        for definition in self.get_klass_definitions():
            self._body.append(self.klass(definition))

        # Generate root definition
        root_definition = self.get_root_definition()

        if "title" in root_definition:
            self._body.append(self.klass(root_definition))

        return self

    def module_imports(self):
        return [
            ast.ImportFrom(
                module="__future__",
                level=0,
                names=[
                    ast.alias(name="unicode_literals", asname=None),
                    ast.alias(name="print_function", asname=None),
                    ast.alias(name="division", asname=None),
                ],
            )
        ]

    def klass(self, definition):
        # Build class properties
        class_body = []
        properties = definition.get("properties")

        if properties:
            required = definition.get("required", ())

            class_body.append(self.get_klass_constructor(properties, required))
        else:
            class_body.append(ast.Pass())

        # Create class definition
        class_def = ast.ClassDef(
            name=definition["title"],
            bases=[ast.Name(id="object")],
            body=class_body,
            decorator_list=[],
            keywords=[],
        )

        # Add to module's body
        return class_def

    def get_key_from_data_object(self, k):
        return ast.Call(
            func=ast.Attribute(value=ast.Name(id="data"), attr="get"),
            args=[ast.Str(s=k)],
            keywords=[],
            starargs=None,
            kwargs=None,
        )

    def _get_default_for_property(self, name, definition):
        def ast_from_dict(d):
            keys = []
            values = []

            for k, v in d.items():
                keys.append(ast.Str(s=k))
                values.append(ast.Num(n=v))

            return ast.Dict(keys=keys, values=values)

        # Get compare's body
        type_ = definition.get("type")

        if type_ == "integer":
            body = ast.Num(n=definition["default"])
        elif type_ == "array":
            body = ast.List(elts=[ast.Num(n=n) for n in definition["default"]])
        elif type_ == "boolean":
            body = ast.NameConstant(value=definition["default"])
        elif type_ == "string":
            body = ast.Str(s=definition["default"])
        elif type_ == "object":
            body = ast_from_dict(definition["default"])
        else:
            raise NotImplementedError("{}: {} => {}".format(self, name, definition))

        # Return ternary expression
        test = ast.Compare(
            left=self.get_key_from_data_object(name),
            ops=[ast.Is()],
            comparators=[ast.NameConstant(value=None)],
        )

        return ast.IfExp(test=test, body=body, orelse=self.get_key_from_data_object(name))

    def _map_property_if_array(self, property_: PropertyType, value: ast.AST) -> ast.AST:
        """
        If array and `items` has `$ref` wrap it into a list comprehension and map array's elements
        """
        # Exit early if doesn't needs to wrap
        items = property_.get("items")

        if isinstance(items, list):
            # We don't support tuple definition yet
            raise NotImplementedError(
                "Tuple items for type 'array' not supported: {}".format(property_)
            )

        elif isinstance(items, dict):
            if "oneOf" in items:
                ref = items["oneOf"][0].get("$ref")

                if ref is None:
                    return value

                # Don't wrap if type is a primitive
                ref = self.definitions[ref]

                if self.definition_is_primitive_alias(ref):
                    return value

                # Wrap value
                ref_title = ref["title"]

                return ast.ListComp(
                    elt=ast.Call(
                        func=ast.Name(id=ref_title),
                        args=[ast.Name(id="v")],
                        keywords=[],
                        starargs=None,
                        kwargs=None,
                    ),
                    generators=[
                        ast.comprehension(target=ast.Name(id="v"), iter=value, ifs=[], is_async=0)
                    ],
                )

        return value

    def _get_dict_comprehension_for_property(self, key, property_):
        # key, value
        comp_key = ast.Name(id="k")
        comp_value = ast.Call(
            func=ast.Name(id="Value"),
            args=[ast.Name(id="v")],
            keywords=[],
            starargs=None,
            kwargs=None,
        )

        # Generator
        # ref = self.definitions[property_["$ref"]]

        generator = ast.comprehension(
            target=ast.Tuple(elts=[ast.Name(id="k"), ast.Name(id="v")]),
            iter=ast.Call(
                func=ast.Attribute(
                    value=self._get_default_for_property(key, property_), attr="iteritems"
                ),
                args=[],
                keywords=[],
                starargs=None,
                kwargs=None,
            ),
            ifs=[],
            is_async=0,
        )

        # Dit comprehension
        dict_comp = ast.DictComp(key=comp_key, value=comp_value, generators=[generator])

        # Return node
        return dict_comp

    def _get_member_value(self, key, property_):
        additional_properties = property_.get("additionalProperties")

        if additional_properties is not None:
            if "$ref" not in additional_properties:
                raise NotImplementedError(
                    "Scalar types for additionalProperties not supported yet"
                )

            return self._get_dict_comprehension_for_property(key, property_)

        if "default" in property_:
            value = self._get_default_for_property(key, property_)
        else:
            value = self.get_key_from_data_object(key)

        value = self._map_property_if_array(property_, value)

        return value

    def get_klass_constructor(self, properties, required):
        # Prepare body
        fn_body = []

        # Default value for `data` argument
        if len(properties) > 0:
            fn_body.append(
                ast.Assign(
                    targets=[ast.Name(id="data")],
                    value=ast.BoolOp(
                        op=ast.Or(), values=[ast.Name(id="data"), ast.Dict(keys=[], values=[])]
                    ),
                )
            )

        for key in sorted(properties.keys()):
            # Get default value
            property_ = properties[key]
            value = self._get_member_value(key, property_)

            # Build assign expression
            attribute = ast.Assign(
                targets=[ast.Attribute(value=ast.Name(id="self"), attr=key)], value=value
            )

            # Add to body
            fn_body.append(attribute)

        # Bundle function arguments and keywords
        fn_arguments = ast.arguments(
            args=[ast.arg(arg="self", annotation=None), ast.arg(arg="data", annotation=None)],
            vararg=None,
            kwarg=None,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[ast.NameConstant(value=None)],
        )

        # Generate class constructor
        fn_init = ast.FunctionDef(
            name="__init__", args=fn_arguments, body=fn_body, decorator_list=[], returns=None
        )

        # Return constructor
        return fn_init

    def as_ast(self):
        return ast.Module(body=self._body)

    def as_code(self):
        return astor.to_source(self.as_ast())
