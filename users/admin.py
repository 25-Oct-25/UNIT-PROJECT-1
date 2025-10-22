import json
import getpass
from utils.colors import *
from utils.helpers import load_data, save_data
from users.user import User

USERS_FILE = "data/users.json"

games = ['TimeTraveler', 'EscapeRoom']

def verify_admin_login(username: str, password: str, UserClass=None) -> bool:
    """Verify if the given credentials belong to an admin user."""
    users = load_users()
    if username not in users:
        return False
    u = users[username]
    if u.get("role") != "admin":
        return False
    if not UserClass:
        UserClass = User
    return UserClass.verify_password(password, u["password"])

def load_users():
    """Load all users' data from the JSON file."""
    return load_data(USERS_FILE) or {}


def save_users(users: dict):
    """Save all users' data to the JSON file."""
    save_data(USERS_FILE, users)


def admin_menu():
    """Display the admin dashboard for managing users and their data."""
    print("\n👑 Welcome, Admin!")
    users = load_users()

    while True:
        print('''\n╔═════════════════════════════╗
║      👑 ADMIN DASHBOARD     ║
╚═════════════════════════════╝
1. 👥 Show all users
2. 🏆 View user scores
3. 📝 Edit user score
4. 🗑️ Delete user
5. 🎖️ Add achievement to user
0. 🚪 Exit admin
''')

        choice = input("Select an option: ").strip()

        if choice == "1":
            if not users:
                print(YELLOW+"⚠️ No users found."+RESET)
            else:
                print("\nRegistered Users:")
                for name, data in users.items():
                    print(f" - {name} ({data.get('role','user')})")
        
        elif choice == "2":
            username = input("Enter username: ").strip()
            if username in users:
                print(json.dumps(users[username].get("scores", {}), indent=2, ensure_ascii=False))
            else:
                print(RED+"User not found."+RESET)

        elif choice == "3":
            username = input("Enter username: ").strip()
            if username in users:
                game = input("Enter game name As(TimeTraveler, EscapeRoom): ").strip()
                if game not in games:
                    print(RED + 'Game not found.' + RESET)
                else:
                    try:
                        new_score = int(input("Enter new score: "))
                        users[username].setdefault("scores", {})
                        users[username]["scores"][game] = new_score
                        save_users(users)
                        print(GREEN+f"Updated {username}'s {game} score to {new_score}."+RESET)
                    except ValueError:
                        print(YELLOW+"⚠️ Invalid score."+RESET)
            else:
                print(RED+"User not found."+RESET)

        elif choice == "4":
            username = input("Enter username to delete: ").strip()
            if username in users:
                confirm = input(f"Are you sure you want to delete {username}? (y/n): ").strip().lower()
                if confirm == "y":
                    del users[username]
                    save_users(users)
                    print(GREEN+f"🗑️ {username} deleted successfully."+RESET)
            else:
                print(RED+"User not found."+RESET)

        elif choice == "5":
            username = input("Enter username: ").strip()
            if username in users:
                achievement = input("Enter achievement: ").strip()
                users[username].setdefault("achievements", [])
                if achievement not in users[username]["achievements"]:
                    users[username]["achievements"].append(achievement)
                    save_users(users)
                    print(GREEN+f"🏅 Added achievement '{achievement}' to {username}."+RESET)
                else:
                    print(YELLOW + "User already has this achievement." + RESET)
            else:
                print(RED+"User not found."+RESET)
        elif choice == "0":
            print("Exiting admin...")
            break
        else:
            print(YELLOW+"⚠️ Invalid option."+RESET)
