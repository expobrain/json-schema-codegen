from marshmallow import Schema, fields


class TestSchema(Schema):
    x = fields.List(default=[42])
