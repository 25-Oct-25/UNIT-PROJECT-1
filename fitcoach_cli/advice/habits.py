# Path: fitcoach_cli/habits/tracking.py
# Description: Log daily habits (water, sleep, steps) and compute a simple daily score.

from ..core.models import AppState
from datetime import date

def log_habits(state: AppState, water_l: float, sleep_h: float, steps: int) -> None:
    """Append a daily habits entry.

    Args:
        state (AppState): Application state holding the habits log.
        water_l (float): Water intake in liters.
        sleep_h (float): Sleep duration in hours.
        steps (int): Steps count.
    """
    state.habits_log.append({
        "date": date.today().isoformat(),
        "water": water_l,
        "sleep": sleep_h,
        "steps": steps,
    })

def score_today(state: AppState) -> str:
    """Compute a simple score for the most recent habits entry.

    Rules:
        +1 if water >= 3 L
        +1 if 7 <= sleep <= 9 hours
        +1 if steps >= 8000

    Args:
        state (AppState): Application state with the habits log.

    Returns:
        str: Human-readable score and tips.
    """
    if not state.habits_log:
        return "No habits logged yet."

    d = state.habits_log[-1]
    score = 0
    score += 1 if d["water"] >= 3 else 0
    score += 1 if 7 <= d["sleep"] <= 9 else 0
    score += 1 if d["steps"] >= 8000 else 0

    tips = []
    if d["water"] < 3:
        tips.append("Increase water to at least 3L.")
    if not (7 <= d["sleep"] <= 9):
        tips.append("Aim for 7–9 hours of sleep.")
    if d["steps"] < 8000:
        tips.append("Raise steps to 8,000+ per day.")

    return f"Habits score: {score}/3. " + (" | ".join(tips) if tips else "Excellent day!")
