# Path: UNIT-PROJECT-1/fitcoach_cli/plan/export.py
"""CSV export utilities.

Provides a helper to export a weekly training plan to a CSV file that can
be opened in spreadsheet tools or shared with clients/teammates.
"""

import csv
from ..core.models import WeeklyPlan


def export_plan_csv(plan: WeeklyPlan, file_path: str) -> str:
    """Export a weekly plan to a CSV file.

    Writes a header row followed by one row per exercise with columns:
    ``Day``, ``Focus``, ``Exercise``, ``Sets``.

    Args:
        plan (WeeklyPlan): The plan to export. Must not be empty.
        file_path (str): Destination path for the CSV file.

    Returns:
        str: The path to the created CSV file.

    Raises:
        ValueError: If ``plan`` is falsy (no plan to export).
        OSError: If the file cannot be created/written.

    Notes:
        The file is written with UTF-8 encoding and ``newline=''`` to ensure
        correct CSV formatting across platforms.
    """
    if not plan:
        raise ValueError("No plan to export.")
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Day", "Focus", "Exercise", "Sets"])
        for wk in plan.workouts:
            for ex in wk.Exercises:
                w.writerow([wk.Day, wk.Focus, ex["name"], ex["sets"]])
    return file_path
