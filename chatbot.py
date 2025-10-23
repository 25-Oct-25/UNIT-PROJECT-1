# chatbot.py
import re
from game import Gamification
from transport import TransportSystem

_greetings = {"hi", "hello", "hey", "hiya"}
_positive = {"good", "great", "fine", "awesome", "well", "happy"}
_negative = {"bad", "sad", "tired", "stressed", "upset", "anxious"}

def detect_mood(text):
    t = text.lower()
    for w in _negative:
        if w in t:
            return "negative"
    for w in _positive:
        if w in t:
            return "positive"
    return "neutral"

def detect_travel_intent(text):
    text = text.lower()
    patterns = [r"\bgo to\b", r"\bgoing to\b", r"\bneed to go\b", r"\bheading to\b", r"\btravel to\b"]
    for pat in patterns:
        if re.search(pat, text):
            return True
    if "commute" in text:
        return True
    return False

class ChatBot:
    def __init__(self, username, data, save_callback=None):
        self.username = username
        self.data = data
        self.save_callback = save_callback
        self.transport = TransportSystem()
        if username not in data:
            data[username] = {"history": [], "score": 0, "streak": 0, "password": ""}

    def chat_loop(self):
        print("\n🤖 Hi! I'm your SmartCommute assistant. Type 'exit' to return.\n")
        while True:
            text = input("You: ").strip()
            if not text:
                continue
            low = text.lower()
            if low in {"exit","quit","bye"}:
                print("Chatbot: Bye! Returning to main menu.")
                break
            if any(low==g or low.startswith(g+" ") for g in _greetings):
                print("Chatbot: Hello! How are you today?")
                continue

            mood = detect_mood(text)
            if mood == "positive":
                print("Chatbot: That's great! Want me to check the best commute? (yes/no)")
                continue
            if mood == "negative":
                print("Chatbot: I'm sorry to hear that 💛. A smooth commute can help — want me to check the best route? (yes/no)")
                continue

            if detect_travel_intent(text):
                ans = input("Chatbot: Sounds like you're going somewhere — should I help plan it? (yes/no)\nYou: ").strip().lower()
                if ans in {"yes","y","sure"}:
                    dest = input("Destination: ")
                    dep_time = input("Departure time (HH:MM): ")
                    weather = input("Weather (clear/sandstorm/hot): ").lower()
                    preference = input("Preference (speed/cost/comfort): ").lower()

                    best, candidates, points, traffic = self.transport.get_best_commute(preference, weather)

                    # Save history
                    record = {
                        "destination": dest,
                        "departure": dep_time,
                        "mode": best["mode"],
                        "time_min": best["time_min"],
                        "cost_sar": best["cost_sar"],
                        "comfort": best["comfort"],
                        "points": points,
                        "weather": weather,
                        "traffic": traffic
                    }
                    self.data.setdefault(self.username, {}).setdefault("history", []).append(record)

                    # Update gamification
                    gm = Gamification(self.username)
                    gm.score = self.data[self.username].get("score",0)
                    gm.streak = self.data[self.username].get("streak",0)
                    gm.add_points(points)
                    self.data[self.username]["score"] = gm.score
                    self.data[self.username]["streak"] = gm.streak

                    if callable(self.save_callback):
                        self.save_callback(self.data)

                    # Show recommendation
                    print(f"Chatbot: ✅ Best commute: {best['mode']} | Time: {best['time_min']} min | Cost: {best['cost_sar']} SAR | Comfort: {best['comfort']}")
                    print(f" - Destination: {dest}  •  Departure: {dep_time}")
                    print(f" - Weather: {weather}  •  Traffic: {traffic}")
                    print(" - Explanation: Combines time, cost, comfort, and your preference to pick the best option.\n")
                    continue
                else:
                    print("Chatbot: Alright — I'm here if you change your mind.")
                    continue

            if "history" in low:
                history = self.data.get(self.username, {}).get("history", [])
                if not history:
                    print("Chatbot: No history yet.")
                else:
                    print("Chatbot: 📜 Your last 5 commutes:")
                    for h in history[-5:]:
                        print(f" - To {h['destination']} at {h['departure']} → {h['mode']} ({h['time_min']} min, {h['cost_sar']} SAR)")
                continue

            print("Chatbot: I can help plan commutes or show history. Say 'best commute' to start or 'history' to view past trips.")

