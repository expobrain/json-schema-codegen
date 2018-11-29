from marshmallow import Schema, fields


class MyTypeSchema(Schema):
    v = fields.Number()


class TestSchema(Schema):
    x = fields.List(fields.Nested(MyTypeSchema), required=True, default=[])
