# Path: fitcoach_cli/training/workouts.py
# Description: Utilities to record workout entries and fetch recent sessions.

from typing import Dict, List
from ..core.models import AppState

def log_workout(state: AppState, day: int, ex: str, weight: float, reps: int, RPE: float) -> None:
    """Append a workout entry to the state log.

    Args:
        state (AppState): Application state holding the workouts log.
        day (int): Day index in the plan (e.g., 1..7).
        ex (str): Exercise name.
        weight (float): Weight used.
        reps (int): Repetitions performed.
        RPE (float): Rate of Perceived Exertion.
    """
    state.workouts_log.append({
        "date": __import__("datetime").date.today().isoformat(),
        "day": day,
        "ex": ex,
        "weight": weight,
        "reps": reps,
        "RPE": RPE
    })

def last_sessions(state: AppState, ex: str, n: int = 5) -> List[Dict]:
    """Get the last n sessions for a specific exercise.

    Args:
        state (AppState): Application state with the workouts log.
        ex (str): Exercise name to search for (case-insensitive).
        n (int): Maximum number of entries to return.

    Returns:
        List[Dict]: Recent matching log entries, newest first.
    """
    return [e for e in state.workouts_log[::-1] if e["ex"].lower() == ex.lower()][:n]
