from __future__ import unicode_literals

from collections import OrderedDict
import json


def load_schema(schema_str):
    return json.loads(schema_str, object_pairs_hook=OrderedDict)


class SchemaParser(object):
    def __init__(self, schema, *args, **kwds):
        self.schema = schema
        self.prefix = kwds.get("prefix")
        self.definitions = OrderedDict()

        self.__parse_definitions()

    def __parse_definitions(self):
        definitions = self.schema.get("definitions", {})

        for key, definition in definitions.iteritems():
            new_key = "#/definitions/{}".format(key)
            new_definition = dict(definition)

            if "title" not in new_definition:
                new_definition["title"] = key

            self.definitions[new_key] = new_definition

    def definition_is_primitive_alias(self, definition):
        return definition.get("type") != "object" or len(definition.get("properties", {})) == 0

    def get_klass_definitions(self):
        prefix = self.prefix or ""

        for definition in self.definitions.itervalues():
            if not self.definition_is_primitive_alias(definition):
                new_title = "{}{}".format(prefix, definition["title"])
                definition = dict(definition, title=new_title)

                yield definition

    def get_type_aliases(self):
        return (d for d in self.definitions.itervalues() if self.definition_is_primitive_alias(d))


class BaseGenerator(object):
    _body = None

    def generate(self):
        return self

    def as_code(self):
        raise NotImplementedError(self)

    def as_ast(self):
        raise NotImplementedError(self)
