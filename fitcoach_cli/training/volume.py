from typing import Dict
from ..core.models import WeeklyPlan

EX_TO_MUSCLE = {
    "bench": "Chest",
    "incline": "Chest",
    "ohp": "Shoulders",
    "shoulder": "Shoulders",
    "lateral": "Shoulders",
    "row": "Back",
    "pulldown": "Back",
    "pull-ups": "Back",
    "rdl": "Hamstrings",
    "romanian": "Hamstrings",
    "squat": "Quads",
    "leg press": "Quads",
    "bulgarian": "Quads",
    "leg curl": "Hamstrings",
    "calf": "Calves",
    "biceps": "Biceps",
    "triceps": "Triceps",
    "core": "Core",
}

def count_volume(plan: WeeklyPlan) -> Dict[str, int]:
    vol: Dict[str, int] = {}
    if not plan:
        return vol
    for w in plan.workouts:
        for ex in w.Exercises:
            name = ex["name"].lower()
            for k, m in EX_TO_MUSCLE.items():
                if k in name:
                    vol[m] = vol.get(m, 0) + 1
                    break
    return vol
