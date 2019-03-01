from marshmallow import Schema, fields as fields_, post_load
from typing import Optional, List, Any


class MyTypeSchema(Schema):
    v = fields_.Number()


class MyType(object):
    def __init__(self, mytype: dict):
        self.v: Optional[float] = mytype.get("v")

    def to_json(self):
        return MyTypeSchema(strict=True).dumps(self).data

    def to_dict(self):
        return MyTypeSchema(strict=True).dump(self).data

    @staticmethod
    def from_json(json: str, only=None):
        return MyTypeSchema(strict=True, only=only).loads(json).data


class TestSchema(Schema):
    x = fields_.List(fields_.Nested(MyTypeSchema), required=True, default=[])

    @post_load
    def make_test(self, test):
        return Test(test)


class Test(object):
    def __init__(self, test: dict):
        self.x: List[MyType] = [MyType(el) for el in test.get("x", {})]

    def to_json(self):
        return TestSchema(strict=True).dumps(self).data

    def to_dict(self):
        return TestSchema(strict=True).dump(self).data

    @staticmethod
    def from_json(json: str, only=None):
        return TestSchema(strict=True, only=only).loads(json).data
