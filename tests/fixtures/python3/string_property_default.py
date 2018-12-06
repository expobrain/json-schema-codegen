from marshmallow import Schema, fields as fields_, post_load
from typing import Optional, List, Any


class TestSchema(Schema):
    x = fields_.String(default='42')

    @post_load
    def make_test(self, test):
        return Test(test)


class Test(object):

    def __init__(self, test: dict):
        self.x: str = test.get('x', '42')

    def to_json(self):
        return TestSchema(strict=True).dumps(self).data

    def to_dict(self):
        return TestSchema(strict=True).dump(self).data

    @staticmethod
    def from_json(json: str, only=None):
        return TestSchema(strict=True, only=only).loads(json).data
