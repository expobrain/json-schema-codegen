from json_codegen.core import BaseGenerator
from json_codegen.astlib import python as ast
from json_codegen.generators.python3.imports import make_imports
from json_codegen.generators.python3.klass import make_klass


class Python3MarshmallowGenerator(BaseGenerator):
    def as_ast(self) -> ast.Module:
        body = []

        # Add module imports
        body.extend(make_imports())

        # Generates definitions first
        for definition in self.json_schema.get_klass_definitions():
            body.append(make_klass(self.json_schema, definition))

        # Generate root definition
        root_definition = self.json_schema.get_root_definition()

        if "title" in root_definition:
            body.append(make_klass(self.json_schema, root_definition))

        # Return AST
        return ast.Module(body=body)
