from typing import Iterable

from pathlib import Path
from collections import OrderedDict
import importlib.util
import json

from json_codegen.types import SchemaType, DefinitionType


class GeneratorNotFoundException(Exception):
    pass


class JSONSchema:
    def __init__(self, schema: SchemaType, prefix: str = ""):
        self.schema = schema
        self.prefix = prefix
        self.definitions = OrderedDict()

        self.__parse_definitions()

    def __parse_definitions(self):
        definitions = self.schema.get("definitions", {})

        for key, definition in definitions.items():
            new_key = "#/definitions/{}".format(key)
            new_definition = dict(definition)

            if "title" not in new_definition:
                new_definition["title"] = key

            self.definitions[new_key] = new_definition

    def __apply_prefix(self, definition: DefinitionType) -> DefinitionType:
        title = definition.get("title")

        if title is None:
            return definition

        new_title = "{}{}".format(self.prefix, definition["title"])
        new_definition = dict(definition, title=new_title)

        return new_definition

    def definition_is_primitive_alias(self, definition: DefinitionType) -> bool:
        return definition.get("type") != "object" or len(definition.get("properties", {})) == 0

    def get_root_definition(self) -> DefinitionType:
        return self.__apply_prefix(self.schema)

    def get_klass_definitions(self) -> Iterable[DefinitionType]:
        return (
            self.__apply_prefix(d)
            for d in self.definitions.values()
            if not self.definition_is_primitive_alias(d)
        )

    def get_type_aliases(self) -> Iterable[DefinitionType]:
        return (d for d in self.definitions.values() if self.definition_is_primitive_alias(d))


class BaseGenerator(object):
    def __init__(self, json_schema: JSONSchema):
        self.json_schema = json_schema

    def as_code(self):
        raise NotImplementedError(self)

    def as_ast(self):
        raise NotImplementedError(self)


def load_external_generator(filename: Path):
    module_name = filename.stem
    klass_name = "".join(s.capitalize() for s in module_name.split("_"))
    filename_str = str(filename)

    spec = importlib.util.spec_from_file_location(module_name, filename_str)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        return getattr(module, klass_name)
    except AttributeError:
        raise GeneratorNotFoundException("Class {} not found in {}".format(klass_name, filename))


def load_schema(schema_str: str) -> JSONSchema:
    return JSONSchema(json.loads(schema_str, object_pairs_hook=OrderedDict))
