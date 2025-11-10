from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class Result:
    ok: bool
    msg: str = ""
    data: Dict[str, Any] | None = None
