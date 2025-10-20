# Path: fitcoach_cli/state/storage.py
# Description: Small JSON-based storage for loading and saving app state.

import json
import os
from typing import Any, Dict

DEFAULT_PATH = os.path.expanduser("~/.fitcoach_state.json")

def load_state(path: str = DEFAULT_PATH) -> Dict[str, Any]:
    """Load state from a JSON file.

    Args:
        path (str): File path to read from.

    Returns:
        Dict[str, Any]: State dict (empty dict if file does not exist).
    """
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(data: Dict[str, Any], path: str = DEFAULT_PATH) -> None:
    """Save state to a JSON file.

    Args:
        data (Dict[str, Any]): State to write.
        path (str): File path to write to.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
