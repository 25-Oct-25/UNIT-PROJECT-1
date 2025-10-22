import random
from typing import List, Dict, Tuple
from .ai_bridge import try_generate_with_llm

# ------------------------------------------------------
# Local MCQ fallback question bank
# ------------------------------------------------------
LOCAL_BANK = [
    {
        "q": "What keyword is used to define a function in Python?",
        "options": ["func", "define", "def", "lambda"],
        "answer": "C",
        "level": "easy"
    },
    {
        "q": "Which of the following is an immutable data type?",
        "options": ["list", "set", "tuple", "dict"],
        "answer": "C",
        "level": "medium"
    },
    {
        "q": "What does the 'yield' keyword do in Python?",
        "options": [
            "Stops a loop",
            "Creates a generator",
            "Returns multiple values",
            "Defines a coroutine"
        ],
        "answer": "B",
        "level": "hard"
    },
    {
        "q": "What is the correct file extension for Python files?",
        "options": [".pt", ".pyth", ".py", ".pyt"],
        "answer": "C",
        "level": "easy"
    },
    {
        "q": "Which method adds an element at the end of a list?",
        "options": ["append()", "add()", "insert()", "extend()"],
        "answer": "A",
        "level": "medium"
    },
    {
        "q": "Which statement is used to handle exceptions in Python?",
        "options": ["try/except", "if/else", "switch/case", "for/while"],
        "answer": "A",
        "level": "medium"
    },
    {
        "q": "Which keyword is used to inherit a class in Python?",
        "options": ["super", "inherit", "extends", "class"],
        "answer": "A",
        "level": "hard"
    },
]

# ------------------------------------------------------
# Utility functions
# ------------------------------------------------------
def _pick(pool, k):
    """Return k random unique items from a list."""
    return random.sample(pool, min(k, len(pool)))


def _fallback_questions(n_easy: int, n_med: int, n_hard: int) -> List[Dict[str, str]]:
    """Assemble fallback MCQs by difficulty."""
    q_easy = [q for q in LOCAL_BANK if q["level"] == "easy"]
    q_med = [q for q in LOCAL_BANK if q["level"] == "medium"]
    q_hard = [q for q in LOCAL_BANK if q["level"] == "hard"]

    selected = _pick(q_easy, n_easy) + _pick(q_med, n_med) + _pick(q_hard, n_hard)
    random.shuffle(selected)
    return selected


# ------------------------------------------------------
# Main public functions
# ------------------------------------------------------
def generate_questions_with_source(n_easy: int, n_med: int, n_hard: int) -> Tuple[List[Dict[str, str]], str]:
    """
    Try to generate MCQs using OpenAI; if it fails, use the local question bank.
    Returns (questions, source_label)
    """
    llm_out = try_generate_with_llm(n_easy, n_med, n_hard)
    if llm_out:
        random.shuffle(llm_out)
        return llm_out, "AI-generated (OpenAI MCQ)"
    return _fallback_questions(n_easy, n_med, n_hard), "Local MCQ Bank"


def generate_questions(n_easy: int, n_med: int, n_hard: int) -> List[Dict[str, str]]:
    """Generate MCQs (AI preferred, fallback local)."""
    qs, _ = generate_questions_with_source(n_easy, n_med, n_hard)
    return qs
