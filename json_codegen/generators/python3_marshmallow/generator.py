from re import search
from typing import List

import astor

from json_codegen.astlib import python as ast
from json_codegen.core import SchemaParser, BaseGenerator
from json_codegen.types import PropertyType
from json_codegen.generators.python3_marshmallow.object_generator import ObjectGenerator
from json_codegen.generators.python3_marshmallow.utils import (
    class_name,
    marshmallow_type_map,
    upper_first_letter,
)


class Python3MarshmallowGenerator(SchemaParser, BaseGenerator):
    def generate(self):
        # Add module imports
        self._body = []
        self._body.extend(self.module_imports())

        # Generates definitions first
        for definition in self.get_klass_definitions():
            schema = self.klass(definition)
            self._body.append(schema)
            self._body.append(ObjectGenerator.construct_class(schema))

        # Generate root definition
        root_definition = self.get_root_definition()

        if "title" in root_definition:
            root_schema = self.klass(root_definition)
            post_load_helper = Python3MarshmallowGenerator.construct_dec_post_load(root_schema)

            for node in ast.walk(root_schema):
                if isinstance(node, ast.ClassDef):
                    node.body.append(post_load_helper)

            self._body.append(root_schema)
            self._body.append(ObjectGenerator.construct_class(root_schema))

        return self

    def module_imports(self):
        return [
            ast.ImportFrom(
                module="marshmallow",
                level=0,
                names=[
                    ast.alias(name="Schema", asname=None),
                    ast.alias(name="fields", asname="fields_"),
                    ast.alias(name="post_load", asname=None),
                ],
            ),
            ast.ImportFrom(
                module="typing",
                level=0,
                names=[
                    ast.alias(name="Optional", asname=None),
                    ast.alias(name="List", asname=None),
                    ast.alias(name="Any", asname=None),
                ],
            ),
        ]

    def klass(self, definition):
        # Build class properties
        class_body = []
        properties = definition.get("properties")

        if properties:
            required = definition.get("required", ())
            class_body.extend(self.get_klass_constructor(properties, required))
        else:
            class_body.append(ast.Pass())

        # Create class definition
        class_def = ast.ClassDef(
            name=upper_first_letter(definition["title"]) + "Schema",
            bases=[ast.Name(id="Schema")],
            body=class_body,
            decorator_list=[],
            keywords=[],
        )

        # Add to module's body
        return class_def

    def get_required_arg(self):
        return ast.keyword(arg="required", value=ast.NameConstant(value=True))

    def get_default_arg(self, d):
        return ast.keyword(arg="default", value=d)

    def get_normal_type(self, prop: PropertyType):
        return marshmallow_type_map[prop["type"]], []

    def get_nested_type(self, prop):
        """
        Scrap the definition from the reference string
        """
        nested_schema_name = search("#/definitions/(.*)$", prop["$ref"])
        attr_type = nested_schema_name.group(1)
        attr_args = [ast.Name(id=upper_first_letter(attr_type) + "Schema")]
        return "Dict", attr_args

    def get_key_from_data_object(self, k, prop, required, default=None):
        """
        If the property references a definition, the resulting field
        should be typed as the nesting schema
        """
        if "$ref" in prop:
            attr_type, attr_args = self.get_nested_type(prop)
        else:
            attr_type, attr_args = self.get_normal_type(prop)

        req = []
        if k in required:
            req.append(self.get_required_arg())

        if default is not None:
            req.append(self.get_default_arg(default))

        return self._make_field(attr_type, attr_args, req)

    def _make_field(self, field: str, args: List, keywords: List) -> ast.Call:
        return ast.Call(
            func=ast.Attribute(value=ast.Name(id="fields_"), attr=field),
            args=args,
            keywords=keywords,
            starargs=None,
            kwargs=None,
        )

    def _get_default_for_property(self, name, definition, required):
        def _default_helper(el):
            if isinstance(el, bool):
                return ast.NameConstant(value=el)
            elif isinstance(el, int):
                return ast.Num(n=el)
            elif isinstance(el, list):
                return ast.List(elts=[_default_helper(subel) for subel in el])
            elif isinstance(el, str):
                return ast.Str(s=el)
            else:
                raise NotImplementedError("Default type not handled (List)")

        def _dict_default_helper(d):

            keys = []
            values = []

            for k, v in d.items():
                keys.append(ast.Str(s=k))

                if isinstance(v, bool):
                    values.append(ast.NameConstant(value=v))
                elif isinstance(v, int):
                    values.append(ast.Num(n=v))
                elif isinstance(v, list):
                    values.append(ast.List(elts=[_default_helper(el) for el in v]))
                elif isinstance(v, str):
                    values.append(ast.Str(s=v))
                elif isinstance(v, dict):
                    values.append(_dict_default_helper(v))
                else:
                    raise NotImplementedError("Default type not handled (Dict)")

            return ast.Dict(keys=keys, values=values)

        default = definition["default"]

        body = (
            _dict_default_helper(default)
            if isinstance(default, dict)
            else _default_helper(default)
        )

        return self.get_key_from_data_object(name, definition, required, default=body)

    def _set_item_type_scalar(self, property_: PropertyType, value: ast.AST) -> ast.AST:
        """
        If the property is a primitive array, type the field.List with
        the correct field type
        """
        for node in ast.walk(value):
            if isinstance(node, ast.Call):
                item_properties = property_.get("items")
                if item_properties is None:
                    x = self._make_field(field="Field", args=[], keywords=[])
                else:
                    attr_type, attr_args = self.get_normal_type(item_properties)

                    x = self._make_field(attr_type, args=attr_args, keywords=[])

                node.args = [x] + node.args

        return value

    def _map_property_if_array(self, property_: PropertyType, value: ast.AST) -> ast.AST:
        """
        If array and `items` has `$ref` wrap it into a list comprehension and map array's elements
        """
        # Exit early if doesn't needs to wrap
        property_items = property_.get("items", {})

        if isinstance(property_items, dict) and "oneOf" in property_items:
            refs = (i.get("$ref") for i in property_items["oneOf"])
            refs = [r for r in refs if r is not None]
        elif isinstance(property_items, list):
            refs = [i["$ref"] for i in property_.get("items", []) if "$ref" in i]
        else:
            refs = []

        if property_.get("type") != "array":  # or len(refs) == 0:
            return value

        if len(refs) == 0:
            return self._set_item_type_scalar(property_, value)

        # Only support one custom type for now
        if len(refs) > 1:
            raise NotImplementedError("{}: we only support one $ref per array".format(self))

        # Don't wrap if type is a primitive
        ref = self.definitions[refs[0]]

        if self.definition_is_primitive_alias(ref):
            return self._set_item_type_scalar(property_, value)

        # Where the array type references a definition, make a nested field with
        # the type of the item schema
        ref_title = upper_first_letter(ref["title"])
        for node in ast.walk(value):
            if isinstance(node, ast.Call):
                x = self._make_field("Nested", [ast.Name(id=ref_title + "Schema")], [])
                node.args = [x] + node.args

        return value

    def _get_member_value(self, key, property_, required):
        additional_properties = property_.get("additionalProperties")

        if additional_properties is not None:
            if "$ref" not in additional_properties:
                raise NotImplementedError(
                    "Scalar types for additionalProperties not supported yet"
                )

            raise NotImplementedError("additionalProperties definitions not supported yet")

        if "default" in property_:
            value = self._get_default_for_property(key, property_, required)
        else:
            value = self.get_key_from_data_object(key, property_, required)

        value = self._map_property_if_array(property_, value)

        return value

    def get_klass_constructor(self, properties, required):
        # Prepare body
        body = []

        for key in sorted(properties.keys()):
            # Get default value
            property_ = properties[key]
            value = self._get_member_value(key, property_, required)

            # Build assign expression
            attribute = ast.Assign(targets=[ast.Name(id=key)], value=value)

            # Add to body
            body.append(attribute)

        # Return constructor
        return body

    @staticmethod
    def construct_dec_post_load(schema):
        name = class_name(schema.name)
        name_lower = name.lower()

        fn_args = ast.arguments(
            args=[ast.arg(arg="self", annotation=None), ast.arg(arg=name_lower, annotation=None)],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )

        fn_body = [
            ast.Return(
                value=ast.Call(func=ast.Name(id=name), args=[ast.Name(id=name_lower)], keywords=[])
            )
        ]

        # By convention, the helper loading function is called make_class
        return ast.FunctionDef(
            name="make_" + name_lower,
            args=fn_args,
            body=fn_body,
            decorator_list=[ast.Name(id="post_load")],
            returns=None,
        )

    def as_ast(self):
        return ast.Module(body=self._body)

    def as_code(self):
        return astor.to_source(self.as_ast())
