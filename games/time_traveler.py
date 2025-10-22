from datetime import datetime
from utils.openai_helper import get_historical_event
from utils.art_assets import TRAVELER_LOGO
from utils.colors import *

class TimeTraveler :
    def __init__(self, user) -> None:
        self.user = user
        self.points = 0

    def safe_int_input(prompt, min_val=None, max_val=None, allow_blank=False):
        """
        Reads an integer input safely with optional bounds and blank allowance.
        """
        while True:
            value = input(prompt).strip()
            if allow_blank and value == "":
                return None
            if not value.isdigit():
                print(RED + "⚠️ Please enter numbers only." + RESET)
                continue
            value = int(value)
            if min_val is not None and value < min_val:
                print(RED + f"⚠️ Value must be >= {min_val}." + RESET)
                continue
            if max_val is not None and value > max_val:
                print(RED + f"⚠️ Value must be <= {max_val}." + RESET)
                continue
            return value

    def play(self):
        """
        Play the Time Traveler game.

        Workflow:
        - Prompts the user to enter a year (required) and optionally month and day.
        - Validates inputs to ensure valid date.
        - Retrieves a historical event for that date.
        - Awards points and handles achievements.
        - Offers replay option.
        """
        
        print(TRAVELER_LOGO)

        year = self.safe_int_input("Enter a year to travel to: ", min_val=1000, max_val=2100)
        month = self.safe_int_input("Enter month (1-12) or leave blank: ", min_val=1, max_val=12, allow_blank=True)
        day = self.safe_int_input("Enter day (1-31) or leave blank: ", min_val=1, max_val=31, allow_blank=True)


        if month and day:
            try:
                datetime(year, month, day)
            except ValueError:
                print(RED + "⚠️ Invalid date! Please enter a valid day/month combination." + RESET)
                return self.play()
            

        print(YELLOW + "\nTraveling through time..." + RESET)

        """while True:
            try:
                year = int(input("Enter a year to travel to: "))
                break
            except ValueError:
                print(RED + "Invalid year. Please enter a valid number." + RESET)

        month = input("Enter month (1-12) or leave blank: ").strip()
        month = int(month) if month.isdigit() else None

        day = input("Enter day (1-31) or leave blank: ").strip()
        day = int(day) if day.isdigit() else None"""

        print(YELLOW + "\nTraveling through time..." + RESET)

        
        event = get_historical_event(year, month, day)
        print(GREEN + f"\n📜 Event found: {event}\n" + RESET)

        points = 10
        self.user.add_score("TimeTraveler", points)
        print(GREEN+f"✨ You earned {points} points!"+RESET)
        print(f"⭐ Total TimeTraveler score: {self.user.scores['TimeTraveler']}")

        if points >= 50 and "Master Time Traveler" not in self.user.achievements:
            self.user.add_achievement("Master Time Traveler")
            print(Fore.LIGHTYELLOW_EX+"🏅 Achievement unlocked: Master Time Traveler"+RESET)

        if 1980 <= year <= 1989 and "Time Explorer 1980s" not in self.user.achievements:
            self.user.add_achievement("Time Explorer 1980s")
            print(Fore.LIGHTYELLOW_EX+"🏅 Achievement unlocked: Time Explorer 1980s"+RESET)

        if 1990 <= year <= 1999 and "Time Explorer 1990s" not in self.user.achievements:
            self.user.add_achievement("Time Explorer 1990s")
            print(Fore.LIGHTYELLOW_EX+"🏅 Achievement unlocked: Time Explorer 1990s"+RESET)
        
        if 2000 <= year <= 2009 and "Time Explorer 2000s" not in self.user.achievements:
            self.user.add_achievement("Time Explorer 2000s")
            print(Fore.LIGHTYELLOW_EX+"🏅 Achievement unlocked: Time Explorer 2000s"+RESET)

        again = input("Do you want to travel again? (yes/no): ").lower()
        if again == "yes":
            self.play()
        else:
            print(CYAN + "Returning to the main menu..." + RESET)