from utils.openai_helper import get_historical_event
from utils.colors import *

class TimeTraveler :
    def __init__(self, user) -> None:
        self.user = user
        self.points = 0

    def play(self):
        '''
        Time Traveler Game:
        - The user enters a year (optional: month/day)
        - We tell them a real historical event
        - We give them points for each trip
        '''
        print(GREEN + "\n🕰️ Welcome to Time Traveler!" + RESET)

        while True:
            try:
                year = int(input("Enter a year to travel to: "))
                break
            except ValueError:
                print(RED + "Invalid year. Please enter a valid number." + RESET)

        month = input("Enter month (1-12) or leave blank: ").strip()
        month = int(month) if month.isdigit() else None

        day = input("Enter day (1-31) or leave blank: ").strip()
        day = int(day) if day.isdigit() else None

        print(YELLOW + "\nTraveling through time..." + RESET)
    
        event = get_historical_event(year, month, day)
        print(GREEN + f"\n📜 Event found: {event}\n" + RESET)