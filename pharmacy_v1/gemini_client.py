#try:
    # package context
  #  from pharmacy_v1.config.environment import gemini_api_key
#except Exception:
   # from config.environment import gemini_api_key

import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()  
gemini_api_key = os.getenv("GEMINI_API_KEY","")
import json
from pathlib import Path

# CONFIG — REPLACE WITH REAL API KEY
genai.configure(api_key=gemini_api_key)

# Load inventory (try current dir, then module dir)
inv_path = Path("inventory.json")
if not inv_path.exists():
    inv_path = Path(__file__).resolve().parent / "inventory.json"
with open(inv_path, "r") as f:
    INVENTORY = json.load(f)

# System prompt (JAILBREAK PROOF)
SYSTEM_PROMPT = f"""
You are an assistant inside a MOCK & EDUCATIONAL pharmacy system for a college student graduation project.
YOU ARE NOT A DOCTOR. You MUST ALWAYS SAY THIS: "This is not medical advice."
Your purpose is to *only suggest possible product matches* from the following inventory:

{json.dumps(INVENTORY, indent=2)}

Rules:
- If user asks medical questions, first say: "I am not a medical professional."
- If user is asking general question about products, answer the user with your view on the products in inventory.
- Then *suggest products from inventory only* — never make medical claims.
- If user says "I have a headache", match "pain relief" items.
- STRICTLY never generate treatment instructions, only product suggestions.
- If you don't find relevant product, say "I have no matching items in inventory."
"""

def ask_gemini(user_input: str):
    """Send query to Gemini with strict system prompt."""
    model = genai.GenerativeModel("models/gemini-2.5-flash-lite")
    response = model.generate_content(
        SYSTEM_PROMPT + "\nUser: " + user_input + "\nAssistant:"
    )
    return response.text


if __name__ == "__main__":
    print("⚕ Gemini Product Recommender (NON-MEDICAL, DEMO ONLY)")
    while True:
        user = input("\nYou: ")
        if user.lower() in ("exit", "quit", "bye"):
            print("Exiting.")
            break
        reply = ask_gemini(user)
        print(f"\n Gemini: {reply}")
