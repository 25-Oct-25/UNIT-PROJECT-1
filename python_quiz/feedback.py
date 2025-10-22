from typing import List, Dict
import re

# Simple topic classifier (regex patterns)
TOPIC_PATTERNS = [
    ("slicing/strings", [r"\[.*:.*\]", r"slic", r"'[^']*'\[", r"\"[^\"]*\"\["]),
    ("lists/enumerate", [r"enumerate", r"list\.copy", r"\[.*for.*in.*\]"]),
    ("sets", [r"\bset\b", r"remove duplicates", r"\bin\b.*set"]),
    ("dicts", [r"dict\.get", r"\{.*:.*\}", r"keys\(\)", r"values\(\)"]),
    ("generators/yield", [r"\byield\b", r"generator"]),
    ("files/with", [r"\bwith\b", r"open\(", r"context manager", r"__enter__|__exit__"]),
    ("performance/GIL", [r"\bGIL\b", r"global interpreter lock"]),
    ("basics", [r"\bdef\b", r"print\(", r"type\(", r"len\(", r"==", r"\bis\b"]),
]
TOPIC_TIPS = {
    "slicing/strings": "Review slicing: s[start:end:step]; remember end is exclusive.",
    "lists/enumerate": "Practice enumerate and list comprehensions; predict outputs first.",
    "sets": "Remember sets remove duplicates; membership is usually O(1).",
    "dicts": "Practice dict.get(key, default) vs direct indexing.",
    "generators/yield": "Write a tiny generator with yield and step through with next().",
    "files/with": "Use 'with' for files to ensure automatic close and resource safety.",
    "performance/GIL": "Read a short summary of the GIL and where threading fits.",
    "basics": "Reinforce: def/print/len/==/is and common data types.",
}

def classify_topic(question_text: str) -> str:
    """Infer question topic by pattern matching."""
    q = question_text.lower()
    for topic, patterns in TOPIC_PATTERNS:
        for pat in patterns:
            if re.search(pat, q):
                return topic
    return "basics"

def build_development_feedback(wrong_questions: List[Dict[str, str]], avg_time: float, score: float) -> str:
    """Build a short development plan from wrong answers and timing."""
    if not wrong_questions:
        pace_hint = "Pace is excellent." if avg_time <= 2.5 else "Maintain your pace and focus on precision."
        return f"Development plan: no notable mistakes. {pace_hint}"

    from collections import Counter
    topics = [classify_topic(w['q']) for w in wrong_questions]
    counts = Counter(topics).most_common()

    lines = []
    lines.append("Development plan:")
    for topic, c in counts[:3]:
        tip = TOPIC_TIPS.get(topic, "Review the concept and try a few short exercises.")
        lines.append(f"- {topic}: {tip}")

    if avg_time > 3.5:
        lines.append(f"- Speed note: your average is {avg_time:.2f}s — answer first, then quickly verify to reduce time.")
    else:
        lines.append(f"- Speed note: your average is {avg_time:.2f}s — good rhythm; keep precision high.")

    if score < 70:
        lines.append("- Action: solve 10 short questions today in each weak topic.")
    elif score < 90:
        lines.append("- Action: focus on one weak topic per day and summarize afterward.")
    else:
        lines.append("- Action: maintain level with varied timed drills.")

    return "\n".join(lines)
