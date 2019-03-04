from typing import NewType, Dict, List

import astor

from json_codegen.astlib import python as ast
from json_codegen.core import SchemaParser, BaseGenerator


DefinitionType = NewType("DefinitionType", Dict)
PropertyType = NewType("PropertyType", Dict)
PropertiesType = NewType("PropertiesType", List[PropertyType])
RequiredType = NewType("RequiredType", List)

PYTHON_ANNOTATION_MAP = {"string": "str", "integer": "int", "number": "float", "boolean": "bool"}


class Python3Generator(SchemaParser, BaseGenerator):
    def generate(self):
        # Add module imports
        self._body = []

        self._body.extend(self.make_module_imports())

        # Generates definitions first
        for definition in self.get_klass_definitions():
            self._body.append(self.make_klass(definition))

        # Generate root definition
        root_definition = self.get_root_definition()

        if "title" in root_definition:
            self._body.append(self.make_klass(root_definition))

        return self

    def make_module_imports(self) -> ast.ImportFrom:
        return [
            ast.ImportFrom(
                module="typing",
                names=[
                    ast.alias(name="Dict", asname=None),
                    ast.alias(name="Optional", asname=None),
                    ast.alias(name="List", asname=None),
                    ast.alias(name="Any", asname=None),
                ],
                level=0,
            )
        ]

    def make_klass(self, definition: DefinitionType) -> ast.Call:
        # Build class properties
        class_body = []
        properties = definition.get("properties")

        if properties:
            required = definition.get("required", [])

            class_body.append(self.make_klass_constructor(properties, required))
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

    def get_key_from_data_object(self, k: str) -> ast.Call:
        return ast.Call(
            func=ast.Attribute(value=ast.Name(id="data"), attr="get"),
            args=[ast.Str(s=k)],
            keywords=[],
            starargs=None,
            kwargs=None,
        )

    def get_default_for_property(self, name: str, definition: DefinitionType) -> ast.IfExp:
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
        orelse = self.get_key_from_data_object(name)

        return ast.IfExp(test=test, body=body, orelse=orelse)

    def get_map_property_if_array(self, property_: PropertyType, value: ast.AST) -> ast.ListComp:
        """
        If array has `items` as 'object' type with `$ref`
        wrap it into a list comprehension and map array's elements
        """
        # Exit early if doesn't needs to wrap
        items = property_.get("items")

        if isinstance(items, dict):
            one_of = items.get("oneOf")
            ref = one_of[0]["$ref"] if one_of else None
        elif isinstance(items, list):
            raise NotImplementedError("Tuple for 'array' non supported: {}".format(property_))
        else:
            ref = None

        if property_.get("type") != "array" or ref is None:
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

    def get_dict_comprehension_for_property(
        self, key: str, property_: PropertyType
    ) -> ast.DictComp:
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
        generator = ast.comprehension(
            target=ast.Tuple(elts=[ast.Name(id="k"), ast.Name(id="v")]),
            iter=ast.Call(
                func=ast.Attribute(
                    value=self.get_default_for_property(key, property_), attr="iteritems"
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

    def get_data_value(self, key: str, property_: PropertyType) -> ast.AST:
        additional_properties = property_.get("additionalProperties")

        if additional_properties is not None:
            if "$ref" not in additional_properties:
                raise NotImplementedError(
                    "Scalar types for additionalProperties not supported yet"
                )

            return self.get_dict_comprehension_for_property(key, property_)

        if "default" in property_:
            value = self.get_default_for_property(key, property_)
        else:
            value = self.get_key_from_data_object(key)

        value = self.get_map_property_if_array(property_, value)

        return value

    def get_partial_annotation_from_definition(self, property_: PropertyType) -> ast.AST:
        # Map property type to annotation
        property_type = property_["type"]

        # ...map object
        if property_type == "object":
            if "oneOf" in property_:
                ref = self.definitions[property_["oneOf"][0]["$ref"]]

                if self.definition_is_primitive_alias(ref):
                    annotation = self.get_partial_annotation_from_definition(ref)
                else:
                    annotation = ast.Name(id=ref["title"])
            elif "additionalProperties" in property_:
                object_name = self.definitions[property_["additionalProperties"]["$ref"]]["title"]

                annotation = ast.Subscript(
                    value=ast.Name(id="Dict"),
                    slice=ast.Index(
                        value=ast.Tuple(elts=[ast.Name(id="str"), ast.Name(id=object_name)])
                    ),
                )
            elif "default" in property_:
                annotation = ast.Name(id="Dict")
            else:
                raise NotImplementedError(
                    "Definition for type 'object' not supported".format(property_)
                )

        # ... map array
        elif property_type == "array":
            items = property_.get("items")

            if isinstance(items, dict):

                item_annotation = self.get_partial_annotation_from_definition(items)
            elif isinstance(items, list):
                raise NotImplementedError(
                    "Tuple for 'array' is not supported: {}".format(property_)
                )
            else:
                item_annotation = ast.Name(id="Any")

            annotation = ast.Subscript(
                value=ast.Name(id="List"), slice=ast.Index(value=item_annotation)
            )

        # ... map scalar
        else:
            python_type = PYTHON_ANNOTATION_MAP[property_["type"]]

            annotation = ast.Name(id=python_type)

        # Return
        return annotation

    def get_annotation_from_definition(self, property_: PropertyType) -> ast.AST:
        annotation = self.get_partial_annotation_from_definition(property_)

        # Make annotation optional if no default value
        if "default" not in property_:
            annotation = ast.Subscript(
                value=ast.Name(id="Optional"), slice=ast.Index(value=annotation)
            )

        # Return
        return annotation

    def make_klass_constructor(
        self, properties: PropertiesType, required: RequiredType
    ) -> ast.FunctionDef:
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
            annotation = self.get_annotation_from_definition(property_)
            value = self.get_data_value(key, property_)

            # Build assign expression
            attribute = ast.AnnAssign(
                target=ast.Attribute(value=ast.Name(id="self"), attr=key),
                annotation=annotation,
                value=value,
                simple=0,
            )

            # Add to body
            fn_body.append(attribute)

        # Bundle function arguments and keywords
        fn_arguments = ast.arguments(
            args=[
                ast.arg(arg="self", annotation=None),
                ast.arg(
                    arg="data",
                    annotation=ast.Subscript(
                        value=ast.Name(id="Optional"), slice=ast.Index(value=ast.Name(id="Dict"))
                    ),
                ),
            ],
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
