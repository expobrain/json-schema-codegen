from marshmallow import Schema, fields


class TestSchema(Schema):
    x = fields.String(default="42")

