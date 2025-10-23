# Path: fitcoach_cli/training/load_suggestions.py
# Description: Suggest a next-session load for an exercise based on recent history.

from ..core.models import AppState

def suggest_loads(state: AppState, ex: str) -> str:
    """Suggest the next load for an exercise using simple rules.

    Looks at the last logged set for the exercise and:
    - Increases ~3% if reps are high and RPE is low (good performance).
    - Decreases ~3% if reps are low and RPE is very high (near failure).
    - Otherwise, keeps the same load.

    Args:
        state (AppState): App state containing the workouts log.
        ex (str): Exercise name to evaluate.

    Returns:
        str: Human-readable recommendation string.
    """
    hist = [e for e in state.workouts_log if e["ex"].lower() == ex.lower()]
    if not hist:
        return "No history for this exercise. Start conservative and +2.5–5% weekly."
    last = hist[-1]
    rec = last["weight"]
    note = "Keep load."
    if last["reps"] >= 10 and last["RPE"] <= 8.0:
        rec = round(last["weight"] * 1.03, 1)
        note = "Great performance; increase ~3% next session."
    elif last["reps"] <= 5 and last["RPE"] >= 9.5:
        rec = round(max(last["weight"] * 0.97, 0), 1)
        note = "Near failure; deload ~3%."
    return f"Last: {last['weight']}x{last['reps']} @RPE{last['RPE']} → Next: ~{rec} kg. {note}"
