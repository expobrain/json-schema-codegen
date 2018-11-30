from marshmallow import Schema, fields as fields_, post_load
from typing import Optional, List


class TestSchema(Schema):
    x = fields_.Integer(default=42)

    @post_load
    def make_test(self, test):
        return Test(test)


class Test(object):
    def __init__(self, test: dict):
        self.x: Optional[int] = test.get("x")

    def to_json(self):
        return TestSchema(strict=True).dumps(self).data

    def to_dict(self):
        return TestSchema(strict=True).dump(self).data
