from marshmallow import Schema, fields


class TestSchema(Schema):
    x = fields.Dict(default={'x': 42})
