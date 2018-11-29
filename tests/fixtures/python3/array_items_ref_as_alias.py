from marshmallow import Schema, fields


class MyType(Schema):
    type = fields.String()


class TestSchema(Schema):
    x = fields.List(fields.Nested(MyType))
