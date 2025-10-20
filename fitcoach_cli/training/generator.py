# Path: fitcoach_cli/training/plan_generator.py
# Description: Build a weekly workout plan (Upper/Lower, Full Body, or PPL) for a given number of days.

from typing import List
from ..core.models import Workout, WeeklyPlan

UPPER = [
    {"name": "Bench Press", "sets": "4x6-8"},
    {"name": "Row (Cable/Barbell)", "sets": "4x8-10"},
    {"name": "OHP / DB Shoulder Press", "sets": "3x8-10"},
    {"name": "Lat Pulldown / Pull-ups", "sets": "3x8-12"},
    {"name": "Incline DB Press", "sets": "3x10-12"},
    {"name": "Lateral Raise", "sets": "3x12-15"},
    {"name": "Triceps Pushdown", "sets": "3x10-12"},
    {"name": "Biceps Curl", "sets": "3x10-12"},
]

LOWER = [
    {"name": "Squat (Back/Front)", "sets": "4x5-8"},
    {"name": "Romanian Deadlift", "sets": "3x6-10"},
    {"name": "Leg Press / Bulgarian Split Squat", "sets": "3x10-12"},
    {"name": "Leg Curl", "sets": "3x10-12"},
    {"name": "Calf Raise", "sets": "4x10-15"},
    {"name": "Core (Plank)", "sets": "3x45-60s"},
]

FULL = [
    {"name": "Squat", "sets": "4x5-8"},
    {"name": "Bench Press", "sets": "4x6-8"},
    {"name": "Row", "sets": "4x8-10"},
    {"name": "RDL", "sets": "3x6-10"},
    {"name": "OHP", "sets": "3x8-10"},
    {"name": "Core", "sets": "3x60s"},
]

def generate_plan(split: str = "upper-lower", days: int = 4) -> WeeklyPlan:
    """Generate a simple weekly workout plan.

    Supports three splits:
    - "upper-lower": Alternates Upper and Lower days.
    - "full-body": Same full-body template each day.
    - "ppl": Push / Pull / Legs cycle.

    Args:
        split (str): Type of split ("upper-lower", "full-body", or "ppl").
        days (int): Number of training days to include.

    Returns:
        WeeklyPlan: Plan object with days, focus, and exercises.
    """
    split = split.lower()
    workouts: List[Workout] = []
    if split == "upper-lower":
        seq = ["Upper", "Lower"] * ((days + 1) // 2)
        seq = seq[:days]
        for i, day in enumerate(seq, 1):
            workouts.append(
                Workout(Day=f"Day {i}", Focus=day, Exercises=UPPER if day == "Upper" else LOWER)
            )
    elif split == "full-body":
        for i in range(1, days + 1):
            workouts.append(Workout(Day=f"Day {i}", Focus="Full Body", Exercises=FULL))
    elif split == "ppl":
        cycle = ["Push", "Pull", "Legs"]
        template = {
            "Push": [
                {"name": "Bench Press", "sets": "4x6-8"},
                {"name": "OHR", "sets": "3x8-10"} if False else {"name": "OHP", "sets": "3x8-10"},
                {"name": "Incline DB Press", "sets": "3x10-12"},
                {"name": "Lateral Raise", "sets": "3x12-15"},
                {"name": "Triceps Pushdown", "sets": "3x10-12"},
            ],
            "Pull": [
                {"name": "Row", "sets": "4x8-10"},
                {"name": "Lat Pulldown", "sets": "3x8-12"},
                {"name": "Face Pull", "sets": "3x12-15"},
                {"name": "Biceps Curl", "sets": "3x10-12"},
            ],
            "Legs": [
                {"name": "Squat", "sets": "4x5-8"},
                {"name": "RDL", "sets": "3x6-10"},
                {"name": "Leg Press", "sets": "3x10-12"},
                {"name": "Calf Raise", "sets": "4x10-15"},
            ],
        }
        seq = [cycle[i % 3] for i in range(days)]
        for i, day in enumerate(seq, 1):
            workouts.append(Workout(Day=f"Day {i}", Focus=day, Exercises=template[day]))
    else:
        return generate_plan("upper-lower", days)
    return WeeklyPlan(split=split, days=days, workouts=workouts)
