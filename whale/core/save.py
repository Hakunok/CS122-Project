import json
from pathlib import Path
from typing import Optional
from core.game_state import GameEngine

SAVE_PATH = Path("whale_save.json")

def save_run(engine: GameEngine) -> None:
    data = engine.to_dict()
    SAVE_PATH.write_text(json.dumps(data))

def load_run() -> Optional[GameEngine]:
    if not SAVE_PATH.exists():
        return None
    data = json.loads(SAVE_PATH.read_text())
    return GameEngine.from_dict(data)

def has_save() -> bool:
    return SAVE_PATH.exists()

def clear_save() -> None:
    if SAVE_PATH.exists():
        SAVE_PATH.unlink()

