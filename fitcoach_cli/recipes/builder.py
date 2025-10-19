from typing import List, Dict, Tuple
from .catalog import RECIPES

def build_day(target_kcal:int, P:int, C:int, F:int, filters:List[str]|None=None) -> Tuple[List[Dict], Dict[str,int]]:
    """Greedy selection of up to 4 recipes approximating targets."""
    pool = RECIPES[:]
    if filters:
        fl = [f.lower() for f in filters]
        pool = [r for r in pool if any(t.lower() in fl for t in r.get("tags", []))] or RECIPES[:]
    picks = []
    totals = {"kcal":0,"protein":0,"carbs":0,"fat":0}
    for _ in range(4):
        best = None; best_score = 1e9
        for r in pool:
            dk = abs((totals["kcal"]+r["kcal"]) - target_kcal)
            dp = max(0, P - (totals["protein"]+r["protein"]))
            score = dk + dp*8
            if score < best_score:
                best = r; best_score = score
        if best:
            picks.append(best)
            totals["kcal"] += best["kcal"]
            totals["protein"] += best["protein"]
            totals["carbs"] += best["carbs"]
            totals["fat"] += best["fat"]
    return picks, totals
