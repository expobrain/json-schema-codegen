from marshmallow import Schema, fields as fields_, post_load
from typing import Optional, List, Any


class TestSchema(Schema):
    id = fields_.Integer(required=True)
    name = fields_.String()

    @post_load
    def make_test(self, test):
        return Test(test)


class Test:
    def __init__(self, test: dict):
        self.id: int = test["id"]
        self.name: Optional[str] = test.get("name")

    def to_json(self):
        return TestSchema(strict=True).dumps(self).data

    def to_dict(self):
        return TestSchema(strict=True).dump(self).data

    @staticmethod
    def from_json(json: str, only=None):
        return TestSchema(strict=True, only=only).loads(json).data
