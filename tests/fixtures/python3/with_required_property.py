from typing import Dict, Optional, List, Any


class Test:
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.id: int = data["id"]
