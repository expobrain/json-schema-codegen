import astor
from re import search

from json_codegen.ast import python as ast
from json_codegen.core import SchemaParser, BaseGenerator
from json_codegen.generators.python3object import Python3ObjectGenerator

type_map = {
    "integer": "Integer",
    "string": "String",
    "boolean": "Boolean",
    "array": "List",
    "number": "Number",
    "object": "Dict",
}


def upper_first_letter(s):
    """
    Assumes custom types of two words are defined as customType
    such that the class name is CustomTypeSchema
    """
    return s[0].upper() + s[1:]


def print_as_code(x):
    print(astor.to_source(ast.Module(body=[x])))


class Python3Generator(SchemaParser, BaseGenerator):
    def generate(self):
        # Add module imports
        self._body = []
        self._body.extend(self.module_imports())

        # Generates definitions first
        for definition in self.get_klass_definitions():
            schema = self.klass(definition)
            self._body.append(schema)
            self._body.append(Python3ObjectGenerator.construct_class(schema))

        # Generate root definition
        root_definition = self.get_root_definition()

        if "title" in root_definition:
            root_schema = self.klass(root_definition)
            self._body.append(root_schema)
            self._body.append(Python3ObjectGenerator.construct_class(root_schema))
            self._body.append(Python3ObjectGenerator.construct_class_post_load_helper(root_schema))

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
            )
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

    def generate_object(self, schema):
        pass

    def get_required_arg(self):
        return ast.keyword(arg="required", value=ast.NameConstant(value=True))

    def get_default_arg(self, d):
        return ast.keyword(arg="default", value=d)

    def get_normal_type(self, prop):
        return type_map[prop["type"]], []

    def get_nested_type(self, prop):
        """
        Scrap the definition from the reference string
        """
        nested_schema_name = search("#/definitions/(.*)$", prop["$ref"])
        attr_type = nested_schema_name.group(1)
        attr_args = [ast.Name(id=attr_type + "Schema")]
        return attr_type, attr_args

    def get_key_from_data_object(self, k, prop, required, default=None):

        # If the property references a definition, the resulting field
        #  should be typed as the nesting schema
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

    def _make_field(self, field, args, keywords):
        return ast.Call(
            func=ast.Attribute(value=ast.Name(id="fields_"), attr=field),
            args=args,
            keywords=keywords,
            starargs=None,
            kwargs=None,
        )

    def _get_default_for_property(self, name, definition, required):
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

        return self.get_key_from_data_object(name, definition, required, default=body)

    def _set_item_type_scalar(self, property_, value):
        """
        If the property is a primitive array, type the field.List with
        the correct field type
        """
        for node in ast.walk(value):
            if isinstance(node, ast.Call):
                item_properties = property_.get("items", {})
                if item_properties != {}:
                    x = self.get_key_from_data_object(None, property_["items"][0], required=[])
                    node.args = [x] + node.args
        return value

    def _map_property_if_array(self, property_, value):
        """
        If array and `items` has `$ref` wrap it into a list comprehension and map array's elements
        """
        # Exit early if doesn't needs to wrap
        refs = [i["$ref"] for i in property_.get("items", ()) if "$ref" in i]

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
            return value

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

            return self._get_dict_comprehension_for_property(key, property_)

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

    def as_ast(self):
        return ast.Module(body=self._body)

    def as_code(self):
        return astor.to_source(self.as_ast())
