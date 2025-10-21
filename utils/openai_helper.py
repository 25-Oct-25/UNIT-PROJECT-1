import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

# ----------------------------
#        Time Traveler 
# ----------------------------

def get_historical_event(year, month=None, day=None):
    '''Generate Event For Game Time Traveler'''
    date_str = f"{year}"
    if month:
        date_str += f"-{month}"
    if day:
        date_str += f"-{day}"

    prompt = (
        f"Give me a **real historical event** that happened on {date_str}. "
        f"It should be fun, positive, or interesting — like discoveries, inventions, pop culture, or sports. "
        f"❌ Do NOT include politics, wars, deaths, or tragic events. "
        f"Write it in one short and engaging sentence suitable for a time-travel game."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a historian that summarizes real events."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error fetching event: {e}"
    

# ----------------------------
#        Escape Room 
# ----------------------------

def generate_puzzle(difficulty="medium", theme="mystery mansion"):
    """
    Generate a dynamic escape room puzzle using OpenAI.
    Returns a dictionary with puzzle text, hint, answer, points, and achievement.
    """

    difficulty_points = {
        "easy": random.randint(10, 20),
        "medium": random.randint(25, 40),
        "hard": random.randint(45, 60)
    }

    prompt = f"""
    You are a creative Escape Room puzzle generator.
    Create a {difficulty}-level puzzle set in a {theme}.
    
    The puzzle must:
    - Require reasoning or logic to solve (not random guessing)
    - Have one word clear correct answer
    - Include a short hint
    - Be immersive and fun, not political or tragic
    
    Return JSON only, like this:
    {{
        "puzzle": "The riddle or puzzle text here...",
        "hint": "A small helpful clue...",
        "answer": "The correct answer."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative puzzle designer for a text-based escape room."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        try:
            data = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # fallback if model adds extra text
            text = response.choices[0].message.content
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(text[start:end+1])
            else:
                raise ValueError("Invalid JSON format from AI")

        # Calculate points based on difficulty and randomness
        points = difficulty_points.get(difficulty, 20)

        # Generate fun achievements
        achievements = {
            "easy": ["🗝️ Beginner Solver", "✨ Quick Thinker"],
            "medium": ["🧠 Logic Master", "🔍 Puzzle Explorer"],
            "hard": ["🏆 Mind Bender", "💎 Genius Escapist"]
        }
        achievement = random.choice(achievements[difficulty])

        return {
            "puzzle": data["puzzle"],
            "hint": data["hint"],
            "answer": data["answer"].strip().lower(),
            "points": points,
            "achievement": achievement
        }

    except Exception as e:
        return {
            "puzzle": "⚠️ Error generating puzzle.",
            "hint": "Try again later.",
            "answer": None,
            "points": 0,
            "achievement": None
        }