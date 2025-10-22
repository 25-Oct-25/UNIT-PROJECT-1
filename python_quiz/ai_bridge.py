"""
AI Bridge — connects to OpenAI to generate Python MCQ quiz questions.
If the API key is missing or a call fails, None is returned and local MCQs are used.
"""

import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv  # load environment variables

load_dotenv()

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# ------------------------------------------------------
# PROMPTS — tell the AI exactly how to respond
# ------------------------------------------------------

SYSTEM_PROMPT = """You are a Python multiple-choice quiz generator.
Return ONLY a valid JSON array. Each item must be an object with keys:
- "q": the question text (English, short and clear)
- "options": an array of 4 short options (A–D order)
- "answer": one letter "A","B","C","D" for the correct option
- "level": one of ["easy","medium","hard"]
All questions must be related to Python (syntax, functions, OOP, data types, loops, exceptions, etc.).
STRICTLY return JSON only. No markdown, no explanations, no emojis.
"""

USER_PROMPT_TEMPLATE = """Generate {n} multiple choice Python quiz questions distributed as:
- easy: {n_easy}
- medium: {n_med}
- hard: {n_hard}

Each question must have exactly 4 options labeled A–D.
Return ONLY a pure JSON array of objects with:
["q", "options", "answer", "level"]
"""


# ------------------------------------------------------
# Helper: clean model output
# ------------------------------------------------------

def _extract_json_array(text: str) -> Optional[str]:
    """Extract the first [...] JSON array from text (remove ``` fences if present)."""
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start:end + 1]


# ------------------------------------------------------
# Main: generate MCQs using OpenAI
# ------------------------------------------------------

def try_generate_with_llm(n_easy: int, n_med: int, n_hard: int) -> Optional[List[Dict[str, str]]]:
    """Ask OpenAI to generate MCQs; return parsed list or None if fails."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None

    try:
        client = OpenAI(api_key=api_key)
        n = n_easy + n_med + n_hard
        user_prompt = USER_PROMPT_TEMPLATE.format(n=n, n_easy=n_easy, n_med=n_med, n_hard=n_hard)

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        raw = resp.choices[0].message.content or ""
        json_text = _extract_json_array(raw) or raw

        data = json.loads(json_text)
        if not isinstance(data, list):
            return None

        # Validate all items
        valid_levels = {"easy", "medium", "hard"}
        out: List[Dict[str, str]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if not all(k in item for k in ("q", "options", "answer", "level")):
                continue
            if item["level"].lower() not in valid_levels:
                continue
            out.append({
                "q": str(item["q"]).strip(),
                "options": item["options"],
                "answer": str(item["answer"]).strip().upper(),
                "level": str(item["level"]).strip().lower(),
            })

        return out if out else None

    except Exception as e:
        # Uncomment for debugging:
        # print(f"AI generation failed: {e}")
        return None
