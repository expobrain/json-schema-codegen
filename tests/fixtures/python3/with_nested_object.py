# isort: skip_file
from typing import Dict, Optional, List, Any  # noqa: F401


class Nested:
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.x: Optional[str] = data.get("x")


class Test:
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.nested: Optional[Nested] = (
            None if data.get("nested") is None else Nested(data.get("nested"))
        )
