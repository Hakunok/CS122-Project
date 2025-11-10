from __future__ import annotations
# Simple target curve (not Balatro's numbers)
def target_for(ante: int, blind_type: str) -> int:
    base = 80 + (ante-1) * 60
    if blind_type == "Small":
        return int(base * 0.75)
    if blind_type == "Big":
        return base
    # Boss
    return int(base * 1.25)
