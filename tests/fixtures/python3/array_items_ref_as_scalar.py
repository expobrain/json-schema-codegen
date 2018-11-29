from marshmallow import Schema, fields


class TestSchema(Schema):
    x = fields.List(fields.String(), required=True, default=[])
