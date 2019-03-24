from typing import Dict, Optional, List, Any


class Test:
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.x: Dict = {"x": 42} if data.get("x") is None else data.get("x")
