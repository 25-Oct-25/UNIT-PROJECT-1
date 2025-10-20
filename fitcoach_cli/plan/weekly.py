# Path: fitcoach/reports/weekly_summary.py
# تعريف: دالة تلخيص سريعة لعرض خطة أسبوعية (workouts) بشكل نصّي منسق.

from ..core.models import WeeklyPlan

def summarize(plan: WeeklyPlan) -> str:
    """Summarize a WeeklyPlan into a readable multi-line string.

    This helper produces a compact text report showing the plan split,
    total days, each workout's day/focus, and its exercises with set counts.

    Args:
        plan (WeeklyPlan): The weekly training plan object containing split,
            days, workouts, and their exercises.

    Returns:
        str: A formatted string summary of the weekly plan.
    """
    lines = [f"Plan: {plan.split} | Days: {plan.days}", "-" * 40]
    for w in plan.workouts:
        lines.append(f"{w.Day} - {w.Focus}")
        for ex in w.Exercises:
            lines.append(f"  - {ex['name']}  ({ex['sets']})")
        lines.append("")
    return "\n".join(lines)
