from marshmallow import Schema, fields


class TestSchema(Schema):
    x = fields.Boolean(default=True)
