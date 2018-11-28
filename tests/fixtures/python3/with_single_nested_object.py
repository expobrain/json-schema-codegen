from marshmallow import Schema, fields


class NestedSchema(Schema):
    x = fields.String()


class TestSchema(Schema):
    nested = fields.Nested(NestedSchema)
