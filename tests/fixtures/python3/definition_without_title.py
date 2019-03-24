from typing import Dict, Optional, List, Any


class NoTitle:
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.x: Optional[str] = data.get("x")
