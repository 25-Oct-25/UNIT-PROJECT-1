# Path: fitcoach_cli/recipes/catalog.py
# Description: Recipe catalog and a simple helper to suggest recipes by kcal/protein and optional tags.

from typing import List, Dict

RECIPES = [
    {"name": "Chicken & Rice Bowl", "kcal": 700, "protein": 50, "carbs": 85, "fat": 18, "tags": ["chicken", "rice", "meal"]},
    {"name": "Beef Wrap", "kcal": 650, "protein": 45, "carbs": 70, "fat": 20, "tags": ["beef", "wrap"]},
    {"name": "Protein Oats", "kcal": 450, "protein": 30, "carbs": 60, "fat": 10, "tags": ["oats", "breakfast"]},
    {"name": "Greek Yogurt & Fruit", "kcal": 300, "protein": 25, "carbs": 40, "fat": 4, "tags": ["snack", "yogurt"]},
    {"name": "Tuna Pasta", "kcal": 600, "protein": 40, "carbs": 80, "fat": 12, "tags": ["tuna", "pasta"]},
]

def suggest(kcal: int, protein: int, filters: List[str] | None = None) -> List[Dict]:
    """Suggest up to 5 recipes near the kcal target and meeting protein needs.

    Args:
        kcal (int): Target calories (±150 range).
        protein (int): Minimum protein (recipe can be within -10g of this).
        filters (List[str] | None): Optional tags to include (any match).

    Returns:
        List[Dict]: Up to five matching recipe dicts.
    """
    res: List[Dict] = []
    for r in RECIPES:
        if abs(r["kcal"] - kcal) <= 150 and r["protein"] >= protein - 10:
            if filters:
                tags = [t.lower() for t in r.get("tags", [])]
                if not any(f.lower() in tags for f in filters):
                    continue
            res.append(r)
    return res[:5]
