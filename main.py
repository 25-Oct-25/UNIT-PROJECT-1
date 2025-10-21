import os
import getpass
from utils.colors import *
from utils.helpers import animated_welcome, load_data, save_data
from users.user import User
from games.time_traveler import TimeTraveler
from games.escape_room import EscapeRoom

USERS_FILE = "data/users.json"

def login_or_register():
    """
    Prompt the user to either log in or register a new account.

    Workflow:
    - Loads existing users from USERS_FILE.
    - Asks the user for a username.
        - If the username exists:
            - Prompts for password (hidden input).
            - Allows up to 3 attempts.
            - On correct password, returns a User object with existing scores and achievements.
            - On 3 failed attempts, exits the program.
        - If the username does not exist:
            - Prompts the user to set a password.
            - Creates a new User object.
            - Saves the new user to USERS_FILE.
            - Returns the newly created User object.

    Returns:
        User: An instance of the User class representing the logged-in or newly registered user.
    """
    users = load_data(USERS_FILE)
    if users is None:
        users = {}

    print("Welcome to Time Arcade!")
    username = input("Enter your username: ").strip()

    if username in users:
        # login
        for _ in range(3):
            password = getpass.getpass("Enter your password (input is hidden):")
            if users[username]["password"] == password:
                print(GREEN + f"Welcome back, {username}!"+RESET)
                user = User(username, password)
                user.scores = users[username]["scores"]
                user.achievements = users[username]["achievements"]
                return user
            else:
                print(RED + "Incorrect password."+RESET)
        print("Too many failed attempts. Exiting.")
        exit()
    else:
        # register
        print("Creating new account...")
        password = getpass.getpass("Set a password (input is hidden): ")
        user = User(username, password)
        users[username] = {
            "password": password,
            "scores": user.scores,
            "achievements": user.achievements
        }
        save_data(USERS_FILE, users)
        print(GREEN + f"Account created! Welcome, {username}! 🌟"+RESET)
        return user
class GameMenu:
    """
    Represents the main menu for the arcade games.

    Attributes:
        user (User): The currently logged-in user.
        games (dict): A dictionary mapping menu options to game instances.

    Methods:
        show_menu():
            Displays the list of available games.
            Allows the user to select and play games.
            Saves user data (scores and achievements) after each game session or upon exiting.
    """
    def __init__(self, user) -> None:
        self.user = user
        self.games = {
            "1":TimeTraveler(user),
            "2":EscapeRoom(user)
            # still working on other games to add it
        }
    def show_menu(self):
        """
        Display the interactive game menu.

        - Prints available games and menu options.
        - Handles user input for selecting a game or exiting.
        - Plays the selected game if valid.
        - Saves user data (password, scores, achievements) after playing a game or exiting.
        - Displays error messages for invalid selections.

        Returns:
            None
        """
        while True:
            print(YELLOW+'''╔══════════════════════════╗
║     🎮 TIME ARCADE 🎮    ║
╚══════════════════════════╝'''+RESET)
            for key, game in self.games.items():
                print(f"{key}. {game.__class__.__name__}")
            print("0. Exit")

            choice = input("Select a game: ").strip()
            if choice == "0":
                print("Goodbye!")
                # save data user after exiting
                users = load_data(USERS_FILE) or {}
                users[self.user.username] = {
                    "password": self.user.password,
                    "scores": self.user.scores,
                    "achievements": self.user.achievements
                }
                save_data(USERS_FILE, users)
                break
            elif choice in self.games:
                self.games[choice].play()
                # save data after user played
                users = load_data(USERS_FILE) or {}
                users[self.user.username] = {
                    "password": self.user.password,
                    "scores": self.user.scores,
                    "achievements": self.user.achievements
                }
                save_data(USERS_FILE, users)
            else:
                print(RED + "Invalid choice. Try again." + RESET)

# run
if __name__ == "__main__":
    animated_welcome()
    user = login_or_register()
    menu = GameMenu(user)
    menu.show_menu()