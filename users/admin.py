import json
import os
from utils.colors import *

USERS_FILE = "data/users.json"



def load_users():
    '''load user data'''
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    '''Save user data after editing'''
    os.makedirs("data", exist_ok=True)  # Make sure the "data" folder exists.
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)



def admin_menu():
    """
    Display the admin dashboard and allow the admin to manage users.

    Features:
    - View all registered users.
    - View scores of a specific user.
    - Edit a user's game score.
    - Delete a user after confirmation.
    - Add achievements to a user.
    
    The menu is interactive and runs in a loop until the admin chooses to exit.
    Requires admin password verification before access.

    Returns:
        None
    """
    
    print("\n👑 Welcome, Admin!")
    users = load_users()

    while True:
        print('''\n╔═════════════════════════════╗
║       👑 ADMIN DASHBOARD     ║
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
                print("⚠️ No users found.")
            else:
                print("\nRegistered Users:")
                for name in users:
                    print(f" - {name}")

        elif choice == "2":
            username = input("Enter username: ").strip()
            if username in users:
                print(json.dumps(users[username]["scores"], indent=2))
            else:
                print(RED+"User not found."+RESET)

        elif choice == "3":
            username = input("Enter username: ").strip()
            if username in users:
                game = input("Enter game name: ").strip()
                try:
                    new_score = int(input("Enter new score: "))
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
                confirm = input(f"Are you sure you want to delete {username}? (y/n): ").lower()
                if confirm == "y":
                    del users[username]
                    save_users(users)
                    print(f"🗑️ {username} deleted successfully.")
            else:
                print(RED+"User not found."+RESET)

        elif choice == "5":
            username = input("Enter username: ").strip()
            if username in users:
                achievement = input("Enter achievement: ").strip()
                users[username]["achievements"].append(achievement)
                save_users(users)
                print(f"🏅 Added achievement '{achievement}' to {username}.")
            else:
                print(RED+"User not found."+RESET)

        elif choice == "0":
            print("Logging out of admin...")
            break
        else:
            print("⚠️ Invalid option. Try again.")


if __name__ == "__main__":
    password = input("Enter admin password: ").strip()
    if password == "admin123":
        admin_menu()
    else:
        print(RED+"Incorrect password."+RESET)
