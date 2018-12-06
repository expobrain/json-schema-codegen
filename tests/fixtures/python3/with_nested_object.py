from marshmallow import Schema, fields as fields_, post_load
from typing import Optional, List, Any


class NestedSchema(Schema):
    x = fields_.String()


class Nested(object):

    def __init__(self, nested: dict):
        self.x: Optional[str] = nested.get('x')

    def to_json(self):
        return NestedSchema(strict=True).dumps(self).data

    def to_dict(self):
        return NestedSchema(strict=True).dump(self).data

    @staticmethod
    def from_json(json: str, only=None):
        return NestedSchema(strict=True, only=only).loads(json).data


class TestSchema(Schema):
    nested = fields_.Dict()

    @post_load
    def make_test(self, test):
        return Test(test)


class Test(object):

    def __init__(self, test: dict):
        self.nested: Optional[dict] = test.get('nested')

    def to_json(self):
        return TestSchema(strict=True).dumps(self).data

    def to_dict(self):
        return TestSchema(strict=True).dump(self).data

    @staticmethod
    def from_json(json: str, only=None):
        return TestSchema(strict=True, only=only).loads(json).data
