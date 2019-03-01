from typing import Dict, Optional, List, Any


class Value(object):
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.v: Optional[int] = data.get("v")


class Test(object):
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.x: Dict[str, Value] = {
            k: Value(v) for k, v in ({} if data.get("x") is None else data.get("x")).iteritems()
        }
