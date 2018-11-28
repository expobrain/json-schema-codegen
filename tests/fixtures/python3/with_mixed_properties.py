from marshmallow import Schema, fields


class TestSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String()
