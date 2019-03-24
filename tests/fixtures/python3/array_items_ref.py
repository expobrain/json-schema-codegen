from typing import Dict, Optional, List, Any


class MyType:
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.v: Optional[float] = data.get("v")


class Test:
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.x: List[MyType] = [
            MyType(v) for v in ([] if data.get("x") is None else data.get("x"))
        ]
