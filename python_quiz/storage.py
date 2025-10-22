import csv
import json
import os
from datetime import datetime
from typing import List, Tuple, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RESULTS_JSON_PATH = os.path.join(DATA_DIR, "results.json")
RESULTS_CSV_PATH  = os.path.join(DATA_DIR, "results.csv")

def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

def load_all_sessions() -> list:
    _ensure_data_dir()
    if not os.path.exists(RESULTS_JSON_PATH):
        return []
    try:
        with open(RESULTS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _append_csv_rows(timestamp: str, sorted_results: List[Tuple[Any, ...]], source: str) -> str:
    """
    Append per-player rows into results.csv
    Columns: timestamp,player,score,avg_time,label,source
    """
    _ensure_data_dir()
    header = ["timestamp", "player", "score", "avg_time", "label", "source"]
    write_header = not os.path.exists(RESULTS_CSV_PATH)
    with open(RESULTS_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        for (name, score, avg_time, label, _message, _dev_plan) in sorted_results:
            w.writerow([timestamp, name, f"{score:.1f}", f"{avg_time:.2f}", label, source])
    return RESULTS_CSV_PATH

def save_session(players: List[str], sorted_results: List[Tuple[Any, ...]], meta: dict = None, save_csv: bool = True) -> tuple[str, str, str | None]:
    """
    Save a session to results.json and optionally append to results.csv.
    players: original players order/names
    sorted_results: list of tuples (name, score, avg_time, label, message, dev_plan)
    meta: optional dict with extra info (e.g., {"mode":"single-level", "source": "..."} )
    save_csv: whether to also append to CSV
    Return: (json_path, timestamp, csv_path_or_none)
    """
    _ensure_data_dir()
    sessions = load_all_sessions()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source = (meta or {}).get("source", "unknown")

    snapshot = {
        "timestamp": timestamp,
        "players": players,
        "mode": (meta or {}).get("mode", "single-level"),
        "source": source,
        "results_sorted": [
            {
                "name": name,
                "score": score,
                "avg_time": avg_time,
                "label": label,
                "message": message,
                "dev_plan": dev_plan,
            }
            for (name, score, avg_time, label, message, dev_plan) in sorted_results
        ]
    }

    sessions.append(snapshot)
    with open(RESULTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

    csv_path = _append_csv_rows(timestamp, sorted_results, source) if save_csv else None
    return RESULTS_JSON_PATH, timestamp, csv_path


