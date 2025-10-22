import json
import os
from typing import Any, Dict

_DEFAULT = {
    "num_easy": 2,
    "num_medium": 2,
    "num_hard": 1,
    "save_pdf": True,
    "save_csv": True,
    "colors": {
        "easy": "green",
        "medium": "yellow",
        "hard": "red",
        "title": "cyan",
        "ok": "green",
        "warn": "magenta"
    }
}

def load_config() -> Dict[str, Any]:
    """Load config.json from this package folder; return defaults if missing/invalid."""
    here = os.path.dirname(__file__)
    path = os.path.join(here, "config.json")
    cfg = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    # merge shallow for top-level keys; for colors do nested merge
    out = dict(_DEFAULT)
    out.update({k: v for k, v in cfg.items() if k != "colors"})
    colors = dict(_DEFAULT["colors"])
    colors.update(cfg.get("colors", {}) if isinstance(cfg.get("colors"), dict) else {})
    out["colors"] = colors
    return out

def distribution_str(cfg: Dict[str, Any]) -> str:
    return f"{cfg['num_easy']} Easy + {cfg['num_medium']} Medium + {cfg['num_hard']} Hard"

def total_questions(cfg: Dict[str, Any]) -> int:
    return int(cfg["num_easy"]) + int(cfg["num_medium"]) + int(cfg["num_hard"])
