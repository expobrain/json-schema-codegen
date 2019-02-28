from marshmallow import Schema, fields as fields_, post_load
from typing import Optional, List, Any


class NoTitleSchema(Schema):
    x = fields_.String()


class NoTitle(object):
    def __init__(self, notitle: dict):
        self.x: Optional[str] = notitle.get("x")

    def to_json(self):
        return NoTitleSchema(strict=True).dumps(self).data

    def to_dict(self):
        return NoTitleSchema(strict=True).dump(self).data

    @staticmethod
    def from_json(json: str, only=None):
        return NoTitleSchema(strict=True, only=only).loads(json).data
