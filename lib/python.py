from __future__ import unicode_literals, print_function, division


import six
import astor

from .ast import python as ast
from .core import SchemaParser, BaseGenerator


class PythonGenerator(SchemaParser, BaseGenerator):
    def generate(self):
        # Add module imports
        self._body = []

        self._body.extend(self.module_imports())

        # Generates definitions first
        for definition in self.get_klass_definitions():
            self._body.append(self.klass(definition))

        # Generate root definition
        if "title" in self.schema:
            self._body.append(self.klass(self.schema))

        return self

    def module_imports(self):
        return [
            ast.ImportFrom(
                module=b"__future__",
                level=0,
                names=[
                    ast.alias(name=b"unicode_literals", asname=None),
                    ast.alias(name=b"print_function", asname=None),
                    ast.alias(name=b"division", asname=None),
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
            name=definition["title"].encode("ascii"),
            bases=[ast.Name(id=b"object")],
            body=class_body,
            decorator_list=[],
        )

        # Add to module's body
        return class_def

    def get_key_from_data_object(self, k):
        if six.PY2:
            k = unicode(k)

        return ast.Call(
            func=ast.Attribute(value=ast.Name(id=b"data"), attr=b"get"),
            args=[ast.Str(s=k)],
            keywords=[],
            starargs=None,
            kwargs=None,
        )

    def _get_default_for_property(self, name, definition):
        def ast_from_dict(d):
            keys = []
            values = []

            for k, v in d.iteritems():
                keys.append(ast.Str(s=k))
                values.append(ast.Num(n=v))

            return ast.Dict(keys=keys, values=values)

        # Get compare's body
        if definition.get("type") == "integer":
            body = ast.Num(n=definition["default"])

        elif definition.get("type") == "array":
            body = ast.List(elts=[ast.Num(n=n) for n in definition["default"]])
        elif definition.get("type") == "boolean":
            body = ast.Name(id=str(definition["default"]))
        elif definition.get("type") == "string":
            body = ast.Str(s=definition["default"])
        elif definition.get("type") == "object":
            body = ast_from_dict(definition["default"])
        else:
            raise NotImplementedError("{}: {} => {}".format(self, name, definition))

        # Return ternary expression
        test = ast.Compare(
            left=self.get_key_from_data_object(name),
            ops=[ast.Is()],
            comparators=[ast.Name(id=b"None")],
        )

        return ast.IfExp(test=test, body=body, orelse=self.get_key_from_data_object(name))

    def _map_property_if_array(self, property_, value):
        """
        If array and `items` has `$ref` wrap it into a list comprehension and map array's elements
        """
        # Exit early if doesn't needs to wrap
        refs = [i["$ref"] for i in property_.get("items", ()) if "$ref" in i]

        if property_.get("type") != "array" or len(refs) == 0:
            return value

        # Only support one custom type for now
        if len(refs) > 1:
            raise NotImplementedError("{}: we only support one $ref per array".format(self))

        # Don't wrap if type is a primitive
        ref = self.definitions[refs[0]]

        if self.definition_is_primitive_alias(ref):
            return value

        # Wrap value
        ref_title = ref["title"]

        if six.PY2:
            ref_title = ref_title.encode("ascii")

        return ast.ListComp(
            elt=ast.Call(
                func=ast.Name(id=ref_title),
                args=[ast.Name(id=b"v")],
                keywords=[],
                starargs=None,
                kwargs=None,
            ),
            generators=[ast.comprehension(target=ast.Name(id=b"v"), iter=value, ifs=[])],
        )

    def get_klass_constructor(self, properties, required):
        # Prepare body
        fn_body = []

        # Default value for `data` argument
        if len(properties) > 0:
            fn_body.append(
                ast.Assign(
                    targets=[ast.Name(id=b"data")],
                    value=ast.BoolOp(
                        op=ast.Or(), values=[ast.Name(id=b"data"), ast.Dict(keys=[], values=[])]
                    ),
                )
            )

        for key in sorted(properties.iterkeys()):
            if six.PY2:
                key = key.encode("ascii")

            # Get default value
            property_ = properties[key]

            if "default" in property_:
                value = self._get_default_for_property(key, property_)
            else:
                value = self.get_key_from_data_object(key)

            value = self._map_property_if_array(property_, value)

            # Build assign expression
            attribute = ast.Assign(
                targets=[ast.Attribute(value=ast.Name(id=b"self"), attr=key)], value=value
            )

            # Add to body
            fn_body.append(attribute)

        # Bundle function arguments and keywords
        fn_arguments = ast.arguments(
            args=[ast.Name(id=b"self"), ast.Name(id=b"data")],
            vararg=None,
            kwarg=None,
            defaults=[ast.Name(id=b"None")],
        )

        # Generate class constructor
        fn_init = ast.FunctionDef(
            name=b"__init__", args=fn_arguments, body=fn_body, decorator_list=[]
        )

        # Return constructor
        return fn_init

    def as_ast(self):
        return ast.Module(body=self._body)

    def as_code(self):
        return astor.to_source(self.as_ast())
