import json
from pathlib import Path
from typing import Optional
from core.game_state import GameEngine

PACKAGE_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PACKAGE_ROOT / "data"
SAVE_PATH = DATA_DIR / "whale_save.json"

def save_run(engine: GameEngine) -> None:
    data = engine.to_dict()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
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
