# Path: UNIT-PROJECT-1/fitcoach_cli/plan/groceries.py
"""Grocery list helpers.

Turns a set of recipe picks (with tags) into a simple grocery list by
counting ingredient occurrences. Also provides a convenience wrapper that
builds a full eating day then derives its grocery list.
"""

from typing import List, Dict, Optional
from ..recipes.builder import build_day

# Heuristic mapping from recipe tags -> grocery items (Arabic labels)
TAG_TO_ITEMS = {
    "chicken": ["دجاج صدور", "بهارات", "زيت زيتون"],
    "rice": ["أرز بسمتي"],
    "oats": ["شوفان", "حليب قليل الدسم"],
    "yogurt": ["زبادي يوناني"],
    "tuna": ["تونة علب", "مكرونة"],
    "beef": ["لحم مفروم قليل الدهن", "تورتيلا"],
    "snack": ["مكسرات", "فاكهة"],
    "pasta": ["مكرونة قمح صلب"],
    "meal": ["خضار مشكلة"],
    "wrap": ["تورتيلا قمح"],
    "breakfast": ["عسل", "فاكهة"],
}


def grocery_from_recipes(recipes: List[Dict]) -> Dict[str, int]:
    """Aggregate grocery items from a list of recipes.

    For each recipe tag, look up items in ``TAG_TO_ITEMS`` and count how
    many times each item appears across all recipes.

    Args:
        recipes (List[Dict]): Recipe dicts; each may contain a ``"tags"`` list.

    Returns:
        Dict[str, int]: Mapping ``item_name -> count`` suitable for a grocery list.
    """
    items: Dict[str, int] = {}
    for r in recipes:
        for t in r.get("tags", []):
            for it in TAG_TO_ITEMS.get(t, []):
                items[it] = items.get(it, 0) + 1
    return items


def build_grocery_list(
    target_kcal: int,
    P: int,
    C: int,
    F: int,
    filters: Optional[List[str]] = None,
):
    """Build a day of meals and derive a grocery list.

    Uses :func:`recipes.builder.build_day` to pick recipes that approximate the
    calorie/macros targets, then converts those picks into a grocery list.

    Args:
        target_kcal (int): Daily calorie target.
        P (int): Protein grams target.
        C (int): Carbohydrate grams target.
        F (int): Fat grams target.
        filters (Optional[List[str]]): Optional include-only tags (e.g., ``["chicken","rice"]``).

    Returns:
        Tuple[List[Dict], Dict[str, int], Dict[str, int]]:
            * ``picks``: The selected recipes for the day.
            * ``totals``: Aggregated macros (kcal/protein/carbs/fat).
            * ``groceries``: Item counts for shopping.

    """
    picks, totals = build_day(target_kcal, P, C, F, filters)
    groceries = grocery_from_recipes(picks)
    return picks, totals, groceries
