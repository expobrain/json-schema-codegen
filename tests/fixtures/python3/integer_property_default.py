from marshmallow import Schema, fields


class TestSchema(Schema):
    x = fields.Integer(default=42)
