import os
import getpass
import logging
import traceback
from utils.colors import *
from utils.helpers import animated_welcome, load_data, save_data, clear_screen
from users.user import User
from users.admin import admin_menu, verify_admin_login
from games.time_traveler import TimeTraveler
from games.escape_room import EscapeRoom


USERS_FILE = "data/users.json"

LOG_FILE = "logs/error.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR, format="%(asctime)s %(levelname)s: %(message)s")

def safe_input(prompt: str, validator=None, error_msg="Invalid input."):
    """Safely handle user input with optional validation."""
    while True:
        try:
            val = input(prompt)
        except (KeyboardInterrupt, EOFError):
            print("\n" + YELLOW + "Input cancelled. Returning to menu." + RESET)
            return None
        val = val.strip()
        if validator is None or validator(val):
            return val
        print(RED + error_msg + RESET)

def safe_password(prompt="Password: "):
    """Securely get hidden password input from user."""
    try:
        return getpass.getpass(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\n" + YELLOW + "Input cancelled. Returning to menu." + RESET)
        return None
def is_valid_username(u: str):
    """Check if username meets minimum requirements."""
    return bool(u) and len(u) >= 3 and " " not in u

def login_or_register():
    """Handle login or registration flow for users and admins."""
    users = load_data(USERS_FILE) or {}

    print("Welcome to Time Arcade!")

    # ask role first
    while True:
        role = safe_input(
            "Are you an Admin or a User? (admin/user): ",
            validator=lambda x: x.lower() in ("admin", "user"),
            error_msg="Please type 'admin' or 'user'."
        )
        if role is None:
            return None
        role = role.lower()
        break

    # ==========================
    # ADMIN LOGIN SECTION
    # ==========================
    if role == "admin":
        # Admin login: only login allowed (no register)
        username = safe_input("Admin username: ", validator=lambda s: bool(s.strip()), error_msg="Username cannot be empty.")
        if username is None:
            return None

       
        users = load_data(USERS_FILE) or {}

        if username not in users or users[username].get("role") != "admin":
            print(RED + "Invalid admin username." + RESET)
            return None

        stored_hash = users[username]["password"]
        max_attempts = 5
        attempts = 0

        while attempts < max_attempts:
            password = safe_password("Admin password (hidden): ")
            if password is None:
                return None
            try:
                if User.verify_password(password, stored_hash):
                    print(GREEN + f"👑 Welcome back, Admin {username}!" + RESET)
                    stored = users.get(username)
                    user = User.from_dict(stored) if stored else User(username, password, role="admin")
                    return user
                else:
                    attempts += 1
                    print(RED + "Incorrect password." + RESET)
                    if attempts < max_attempts:
                        print(YELLOW + f"Attempt {attempts}/{max_attempts}. Try again." + RESET)
            except Exception as e:
                # if something unexpected happens during verification, log and stop
                logging.error("Admin password verify error: %s\n%s", e, traceback.format_exc())
                print(RED + "⚠️ An error occurred verifying password. See logs." + RESET)
                return None

        # if reached here: too many attempts
        print(RED + "Too many incorrect attempts. Returning to main menu." + RESET)
        return None

    # ==========================
    # USER LOGIN / REGISTER SECTION
    # ==========================
    else:
        """Handle user login or account creation."""
        while True:
            username = safe_input(
                "Enter your username: ",
                validator=is_valid_username,
                error_msg="Username must be at least 3 chars and contain no spaces."
            )
            if username is None:
                return None

            
            reserved_admins = [u for u, v in users.items() if v.get("role") == "admin"]
            if username.lower() == "admin" or username in reserved_admins:
                print(RED + "⚠️ The username 'admin' is reserved. Please choose another username." + RESET)
                continue
            break

        if username in users:
            """Login existing user if credentials match."""
            attempts = 0
            while attempts < 3:
                password = safe_password("Enter your password (hidden): ")
                if password is None:
                    return None
                try:
                    if User.verify_password(password, users[username]["password"]):
                        print(GREEN + f"Welcome back, {username}!" + RESET)
                        return User.from_dict(users[username])
                    else:
                        attempts += 1
                        print(RED + "Incorrect password." + RESET)
                except Exception as e:
                    logging.error("Password verify error for %s: %s\n%s", username, e, traceback.format_exc())
                    print(RED + "⚠️ Error verifying password. See logs." + RESET)
                    return None
            print(RED + "Too many failed attempts. Returning to main menu." + RESET)
            return None

        print("Creating new account...")
        """Register a new user if username not found."""
        while True:
            password = safe_password("Set a password (hidden): ")
            if password is None:
                return None
            if len(password) < 4:
                print(YELLOW + "Password should be at least 4 characters." + RESET)
                continue
            break
        try:
            user = User(username, password, role="user")
            users[username] = user.to_dict()
            save_data(USERS_FILE, users)
            print(GREEN + f"Account created! Welcome, {username}! 🌟" + RESET)
            return user
        except Exception as e:
            logging.error("Error creating user %s: %s\n%s", username, e, traceback.format_exc())
            print(RED + "⚠️ Error creating account. See logs." + RESET)
            return None


class GameMenu:
    """Main game menu allowing users to select and play available games."""
    def __init__(self, user) -> None:
        """Initialize game menu with user and available games."""
        self.user = user
        self.games = {
            "1":TimeTraveler(user),
            "2":EscapeRoom(user)
        }
    def show_menu(self):
        """Display and handle the main game selection menu."""
        while True:
            try:
                clear_screen()
                print(YELLOW+'''╔══════════════════════════╗
║     🎮 TIME ARCADE 🎮    ║
╚══════════════════════════╝'''+RESET)
                for key, game in self.games.items():
                    print(f"{key}. {game.__class__.__name__}")
                if getattr(self.user, "role", "user") == "admin":
                    print("3. 👑 Admin Dashboard")
                print("0. Exit")

                choice = safe_input("Select an option: ")
                if choice is None:
                    return
                choice = choice.strip()
                if choice == "0":
                    print("Goodbye!👋")
                    users = load_data(USERS_FILE) or {}
                    users[self.user.username] = self.user.to_dict()
                    save_data(USERS_FILE, users)
                    return
                elif choice in self.games:
                    """Play selected game and save progress."""
                    try:
                        self.games[choice].play()
                    except Exception as e:
                        logging.error("Error running game %s: %s\n%s", choice, e, traceback.format_exc())
                        print(RED + "⚠️ An error occurred while running the game. See logs." + RESET)
                    finally:
                        users = load_data(USERS_FILE) or {}
                        users[self.user.username] = self.user.to_dict()
                        save_data(USERS_FILE, users)
                elif choice == "3" and getattr(self.user, "role", "user") == "admin":
                    """Open admin dashboard if user is an admin."""
                    try:
                        admin_menu()
                    except Exception as e:
                        logging.error("Admin menu error: %s\n%s", e, traceback.format_exc())
                        print(RED + "⚠️ Admin error. See logs." + RESET)
                else:
                    print(RED + "Invalid choice. Try again." + RESET)
            except (KeyboardInterrupt, EOFError):
                print("\n" + YELLOW + "Interrupted. Returning to main menu." + RESET)
                return
            except Exception as e:
                logging.error("Unexpected error in main menu: %s\n%s", e, traceback.format_exc())
                print(RED + "An unexpected error occurred. Check logs and try again." + RESET)
                safe_input("Press Enter to continue...")


if __name__ == "__main__":
    """Run the Time Arcade program."""
    try:
        animated_welcome()
        user = login_or_register()
        if not user:
            print(YELLOW + "No user logged in. Exiting." + RESET)
        else:
            menu = GameMenu(user)
            menu.show_menu()
    except Exception as e:
        logging.critical("Fatal error on startup: %s\n%s", e, traceback.format_exc())
        print(RED + "A fatal error occurred. See logs." + RESET)