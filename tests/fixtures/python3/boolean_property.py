# isort: skip_file
from typing import Dict, Optional, List, Any  # noqa: F401


class Test:
    def __init__(self, data: Optional[Dict] = None):
        data = data or {}

        self.x: Optional[bool] = data.get("x")
