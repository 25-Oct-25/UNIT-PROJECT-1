# main.py
import os
import sys
import time
import random
import json
from rich.console import Console
from rich.table import Table
from rich import box
from pyfiglet import Figlet
from colorama import init, Fore
from game import Gamification
from chatbot import ChatBot
from transport import TransportSystem

init(autoreset=True)
console = Console()
DATA_FILE = "data.json"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "1234"  # Change this to your preferred admin password
}

# ------------------- Helpers -------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def animated_banner(text, delay=0.02):
    for c in text:
        print(f"{Fore.CYAN}{c}", end="", flush=True)
        time.sleep(delay)
    print("\n")

# ------------------- Transport -------------------
class TransportMode:
    def __init__(self, name, base_time, cost, comfort):
        self.name = name
        self.base_time = base_time
        self.cost = cost
        self.comfort = comfort

    def calculate_time(self, traffic_multiplier=1, weather_multiplier=1):
        return self.base_time * traffic_multiplier * weather_multiplier

class TransportSystem:
    def __init__(self):
        self.modes = [
            TransportMode("Car", 20, 12, "High"),
            TransportMode("Metro", 30, 7, "Medium"),
            TransportMode("Bus", 45, 5, "Low"),
        ]

    def get_best_commute(self, preference="speed", weather="clear"):
        traffic_level = random.choice(["Low","Moderate","Heavy"])
        weather_multiplier_map = {"clear":1.0,"sandstorm":1.5,"hot":1.1}
        t_mult_map = {"Low":1.0,"Moderate":1.3,"Heavy":1.8}
        t_mult = t_mult_map[traffic_level]
        w_mult = weather_multiplier_map.get(weather.lower(), 1.0)

        best_score = -1
        best_candidate = None
        candidates = []

        for m in self.modes:
            est_time = m.calculate_time(t_mult, w_mult)
            if preference=="speed":
                score = 100/est_time
            elif preference=="cost":
                score = 50/m.cost
            elif preference=="comfort":
                score = {"Low":10,"Medium":20,"High":30}[m.comfort]
            else:
                score = 100/est_time

            candidate = {
                "mode": m.name,
                "time_min": round(est_time),
                "cost_sar": m.cost,
                "comfort": m.comfort,
                "score": round(score)
            }
            candidates.append(candidate)
            if score>best_score:
                best_score = score
                best_candidate = candidate

        points = max(0, int(best_score))
        return best_candidate, candidates, points, traffic_level

# ------------------- Main -------------------
def main():
    os.system("cls" if os.name=="nt" else "clear")
    data = load_data()
    transport = TransportSystem()

    # Welcome Screen
    f = Figlet(font="slant")
    console.print(f"{Fore.MAGENTA}{f.renderText('SmartCommute')}", style="bold cyan")
    input(Fore.YELLOW + "Press Enter to start your journey...")

    animated_banner("🚀 Launching Your Smart Commute Engine… Prepare for takeoff… 🚀", delay=0.01)

    # ------------------- Login / Signup -------------------
    username = ""
    while not username:
        choice = input("Do you want to (1) Login or (2) Sign up? ").strip()
        if choice == "1":
            u = input("Username: ").strip()
            p = input("Password: ").strip()

            # Check if admin login
            if u == ADMIN_CREDENTIALS["username"] and p == ADMIN_CREDENTIALS["password"]:
                from admin import AdminPanel
                admin_panel = AdminPanel(data, save_callback=save_data)
                admin_panel.show_panel()
                print("Exiting program.")
                sys.exit()

            # Normal user login
            elif u in data and data[u]["password"] == p:
                username = u
                console.print(f"[green]Welcome back, {username}![/green]")
            else:
                console.print("[red]User not found or wrong password.[/red]")

        elif choice == "2":
            u = input("Choose username: ").strip()
            if u in data or u == ADMIN_CREDENTIALS["username"]:
                console.print("[red]Username already exists or reserved.[/red]")
            else:
                p = input("Create password: ").strip()
                data[u] = {"password": p, "history": [], "score": 0, "streak": 0}
                save_data(data)
                username = u
                console.print(f"[green]Account created. Welcome, {username}![/green]")
        else:
            console.print("[red]Type 1 or 2.[/red]")

    # ------------------- Gamification -------------------
    gm = Gamification(username)
    gm.score = data[username].get("score",0)
    gm.streak = data[username].get("streak",0)

    # ------------------- Main User Loop -------------------
    while True:
        console.print("\n[bold green]Menu[/bold green]")
        console.print("1) Get Best Commute\n2) View Commute History\n3) View Score & Streak\n4) Chatbot\n5) Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            dest = input("Destination: ")
            dep_time = input("Planned departure time (HH:MM): ")
            weather = input("Current weather (clear / sandstorm / hot): ").capitalize()
            preference = input("Preference (speed / cost / comfort): ").lower()
            best, candidates, points, traffic = transport.get_best_commute(preference, weather)

            # Save history
            data[username]["history"].append({
                "destination": dest,
                "departure": dep_time,
                "mode": best["mode"],
                "time_min": best["time_min"],
                "cost_sar": best["cost_sar"],
                "comfort": best["comfort"],
                "points": points,
                "weather": weather,
                "traffic": traffic
            })

            gm.add_points(points)
            data[username]["score"] = gm.score
            data[username]["streak"] = gm.streak
            save_data(data)

            # Show explanation
            console.print("\n[bold green]✅ Recommendation[/bold green]")
            console.print(f"Mode: {best['mode']}  •  Time: {best['time_min']} min  •  Cost: {best['cost_sar']} SAR  •  Comfort: {best['comfort']}")
            console.print("\n[italic yellow]Why this choice?[/italic yellow]")
            console.print(f"- Destination: {dest}  •  Departure: {dep_time}")
            console.print(f"- Weather: {weather}  •  Traffic: {traffic}")
            console.print("- Explanation: Combines time, cost, comfort and your preference to pick the best option.\n")

        elif choice == "2":
            history = data[username].get("history",[])
            if not history:
                console.print("No history yet.", style="yellow")
            else:
                table = Table(title="Commute History", box=box.ROUNDED)
                table.add_column("Mode")
                table.add_column("Time (min)")
                table.add_column("Cost (SAR)")
                table.add_column("Comfort")
                table.add_column("Destination")
                table.add_column("Departure")
                table.add_column("Weather")
                table.add_column("Traffic")
                for h in history:
                    table.add_row(
                        h.get("mode", "N/A"),
                        str(h.get("time_min", "N/A")),
                        str(h.get("cost_sar", "N/A")),
                        h.get("comfort", "N/A"),
                        h.get("destination", "N/A"),
                        h.get("departure", "N/A"),
                        h.get("weather", "Unknown"),
                        h.get("traffic", "Unknown")
                    )
                console.print(table)

        elif choice == "3":
            console.print(f"🎯 Your Score: {gm.score} | Current Streak: {gm.streak}", style="magenta")

        elif choice == "4":
            chatbot = ChatBot(username, data, save_callback=save_data)
            chatbot.chat_loop()
            save_data(data)

        elif choice == "5":
            console.print("Goodbye! 👋", style="green")
            break

        else:
            console.print("Invalid choice", style="red")

if __name__=="__main__":
    main()
