import random

# Motivational/funny/tips
MOTIV = [
    "Strong performance.",
    "Clear and organized thinking.",
    "Consistency leads to improvement.",
    "Solid confidence and steady pace.",
    "Results to be proud of.",
]
FUNNY = [
    "Your code smiles when answers are precise.",
    "Python seems like your daily companion.",
    "Smart and swift analysis.",
    "Your logic reads like clean code.",
]
TIPS = [
    "Tip: use 'with' for safe file handling.",
    "Tip: f-strings are fast and readable.",
    "Tip: sets help remove duplicates and test membership.",
    "Tip: list comprehensions simplify transformations.",
    "Tip: Write code for humans first, computers second, readability is power.",
]

def finalize_message(score: float, avg_time: float) -> str:
    """Compact message based on score/time."""
    if score >= 90:
        head = "Rating: excellent."
    elif score >= 70:
        head = "Rating: fast thinker."
    else:
        head = "Rating: needs more practice."

    part_m = random.choice(MOTIV)
    part_f = random.choice(FUNNY)
    part_t = random.choice(TIPS)
    return f"{head}\n{part_m}\n{part_f}\n{part_t}\nAverage time: {avg_time:.2f}s"
