import json

from json_codegen.core import SchemaParser, BaseGenerator
from json_codegen.astlib import javascript as ast
from json_codegen.js_utils import get_type_annotation


class FlowGenerator(SchemaParser, BaseGenerator):
    def generate(self):
        # Generates type aliases
        self._body = []

        for definition in self.get_type_aliases():
            self._body.append(self.type_alias(definition))

        # Generates definitions
        for definition in self.get_klass_definitions():
            self._body.append(self.klass(definition))

        # Generate root definition
        root_definition = self.get_root_definition()

        if "title" in root_definition:
            self._body.append(self.klass(root_definition))

        # Add leading comment
        if len(self._body):
            self._body[0]["leadingComments"] = [ast.CommentLine("@flow")]

        return self

    def type_alias(self, definition):
        aliased_type = get_type_annotation(self.definitions, definition, required=True)
        type_alias = ast.DeclareTypeAlias(
            id_=ast.Identifier(definition["title"]), right=aliased_type
        )

        return type_alias

    def klass(self, definition):
        # Build class property Flow definition
        klass_annotations = []
        required = definition.get("required", ())
        properties = definition.get("properties", {})

        for key in sorted(properties.keys()):
            # Add property type definition
            property_ = properties[key]
            is_required = key in required
            has_default = "default" in property_

            property_annotation = get_type_annotation(
                self.definitions, property_, required=(is_required or has_default)
            )
            property_def = ast.ObjectTypeProperty(
                key=ast.Identifier(key), value=property_annotation, force_variance=True
            )
            klass_annotations.append(property_def)

        # Add class constructor
        if len(properties):
            klass_annotations.append(self.klass_constructor())

        # Return class definition
        klass = ast.DeclareTypeAlias(
            id_=ast.Identifier(definition["title"]),
            right=ast.ObjectTypeAnnotation(klass_annotations),
        )

        return klass

    def klass_constructor(self):
        return ast.ObjectTypeProperty(
            key=ast.Identifier("constructor"),
            value=ast.FunctionTypeAnnotation(
                params=[
                    ast.FunctionTypeParam(
                        ast.Identifier("data"),
                        type_annotation=ast.NullableTypeAnnotation(
                            ast.GenericTypeAnnotation(ast.Identifier("Object"))
                        ),
                    )
                ],
                return_type=ast.VoidTypeAnnotation(),
            ),
            method=True,
        )

    def as_ast(self):
        return ast.File(program=ast.Program(body=self._body), comments=[ast.CommentLine("@flow")])

    def as_code(self):
        return json.dumps(self.as_ast(), indent=2)
