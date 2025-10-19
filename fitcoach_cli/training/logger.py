from typing import Dict, List
from ..core.models import AppState

def log_workout(state: AppState, day: int, ex: str, weight: float, reps: int, RPE: float):
    state.workouts_log.append({
        "date": __import__("datetime").date.today().isoformat(),
        "day": day,
        "ex": ex,
        "weight": weight,
        "reps": reps,
        "RPE": RPE
    })

def last_sessions(state: AppState, ex: str, n: int = 5) -> List[Dict]:
    return [e for e in state.workouts_log[::-1] if e["ex"].lower() == ex.lower()][:n]
