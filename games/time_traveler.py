from utils.openai_helper import get_historical_event
from utils.colors import *

class TimeTraveler :
    def __init__(self, user) -> None:
        self.user = user
        self.points = 0

    def play(self):
        """
    Play the Time Traveler game.

    Workflow:
    - Prompts the user to enter a year (required) and optionally month and day.
    - Retrieves a real historical event corresponding to the entered date.
    - Awards the user points for completing a time travel trip.
    - Updates the user's score for the "TimeTraveler" game.
    - Checks and unlocks achievements based on points earned or specific year ranges:
        - "Master Time Traveler" for reaching 50 points.
        - "Time Explorer 1980s" for traveling to any year in the 1980s.
        - "Time Explorer 1990s" for traveling to any year in the 1990s.
        - "Time Explorer 2000s" for traveling to any year in the 2000s.
    - Asks the user if they want to play again and repeats if confirmed.

    User Feedback:
        - Displays the historical event found.
        - Shows points earned and total score.
        - Notifies when an achievement is unlocked.

    Input:
        - year (int): The year to travel to.
        - month (int, optional): The month to travel to.
        - day (int, optional): The day to travel to.
        - again (str): User input to play again ("yes" or "no").

    Returns:
        None
    """
        print(PURPLE + "\n🕰️ Time Traveler!" + RESET)

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