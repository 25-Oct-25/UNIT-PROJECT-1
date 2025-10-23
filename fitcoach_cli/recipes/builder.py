# Path: fitcoach_cli/recipes/day_builder.py
# Description: Greedy helper to pick up to 4 recipes that fit calorie and macro goals.

from typing import List, Dict, Tuple
from .catalog import RECIPES

def build_day(target_kcal: int, P: int, C: int, F: int, filters: List[str] | None = None) -> Tuple[List[Dict], Dict[str, int]]:
    """Pick up to 4 recipes that roughly match the daily targets.

    The selection is greedy: each step chooses the recipe that best
    improves the total toward the target calories and protein.
    Optional tag filters can limit the recipe pool.

    Args:
        target_kcal (int): Target total calories for the day.
        P (int): Target protein (grams).
        C (int): Target carbs (grams). (Not directly optimized, tracked in totals.)
        F (int): Target fat (grams). (Not directly optimized, tracked in totals.)
        filters (List[str] | None): Optional list of tag names to include.

    Returns:
        Tuple[List[Dict], Dict[str, int]]:
            - List of selected recipe dicts (up to 4).
            - Totals dict with keys: "kcal", "protein", "carbs", "fat".
    """
    pool = RECIPES[:]
    if filters:
        fl = [f.lower() for f in filters]
        pool = [r for r in pool if any(t.lower() in fl for t in r.get("tags", []))] or RECIPES[:]
    picks = []
    totals = {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}
    for _ in range(4):
        best = None
        best_score = 1e9
        for r in pool:
            dk = abs((totals["kcal"] + r["kcal"]) - target_kcal)
            dp = max(0, P - (totals["protein"] + r["protein"]))
            score = dk + dp * 8
            if score < best_score:
                best = r
                best_score = score
        if best:
            picks.append(best)
            totals["kcal"] += best["kcal"]
            totals["protein"] += best["protein"]
            totals["carbs"] += best["carbs"]
            totals["fat"] += best["fat"]
    return picks, totals
