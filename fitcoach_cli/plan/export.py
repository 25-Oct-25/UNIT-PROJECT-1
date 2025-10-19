import csv
from ..core.models import WeeklyPlan

def export_plan_csv(plan: WeeklyPlan, file_path: str) -> str:
    if not plan:
        raise ValueError("No plan to export.")
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Day","Focus","Exercise","Sets"])
        for wk in plan.workouts:
            for ex in wk.Exercises:
                w.writerow([wk.Day, wk.Focus, ex["name"], ex["sets"]])
    return file_path
