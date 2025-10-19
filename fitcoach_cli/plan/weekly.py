from ..core.models import WeeklyPlan

def summarize(plan: WeeklyPlan) -> str:
    lines = [f"Plan: {plan.split} | Days: {plan.days}", "-"*40]
    for w in plan.workouts:
        lines.append(f"{w.Day} - {w.Focus}")
        for ex in w.Exercises:
            lines.append(f"  - {ex['name']}  ({ex['sets']})")
        lines.append("")
    return "\n".join(lines)
