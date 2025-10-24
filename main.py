#Project imports 
from src.User import User
from src.StoryManager import StoryManager
#External libraries
from colorama import Fore, Style, init


# Enable colors for all terminal types
init(autoreset=True, convert=True)


def main():
    """Main entry point of the Interactive Story App."""
    print(Fore.MAGENTA + "\n" + "💫" + "═" * 46 + "💫")
    print(Fore.CYAN + "🌙  WELCOME TO  🌙".center(60))
    print(Fore.LIGHTWHITE_EX + "AI INTERACTIVE STORY CREATOR".center(60))
    print(Fore.MAGENTA + "💫" + "═" * 46 + "💫" + Style.RESET_ALL)

    user = None

    # Authentication loop
    while not user:
        print(Fore.CYAN + "\n=== 🔐 ACCOUNT MENU ===" + Style.RESET_ALL)
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")

        choice = input(Fore.LIGHTGREEN_EX + "Choose (1/2/3): ").strip()

        if choice == "1":
            user = User.login()
            if not user:
                print(Fore.RED + "\n❌ Login failed.")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry == "n":
                    signup = input(Fore.CYAN + "Would you like to sign up for a new account? (y/n): ").strip().lower()
                    if signup == "y":
                        user = User.signup()
                    else:
                        print(Fore.MAGENTA + "👋 Goodbye! See you next time.")
                        return
        elif choice == "2":
            user = User.signup()
        elif choice == "3":
            print(Fore.MAGENTA + "\n👋 Goodbye! See you next time 🌙")
            return
        else:
            print(Fore.RED + "⚠️ Invalid option. Please choose 1, 2, or 3.")

    # Successfully logged in or signed up
    manager = StoryManager(user.username)

    # Check if there is a previously saved story
    print(Fore.CYAN + "\n🔎 Checking if you have a previous story...")
    try:
        manager.resume_last_story()
    except Exception as e:
        print(Fore.YELLOW + f"⚠️ Could not load previous story: {e}")
        print(Fore.CYAN + "Starting fresh...\n")

    # Main Story Menu
    while True:
        print(Fore.MAGENTA + "\n" + "💫" + "═" * 46 + "💫")
        print(Fore.CYAN + "📚  STORY MENU  📚".center(60))
        print(Fore.MAGENTA + "═" * 50 + "💫")
        print(Fore.LIGHTWHITE_EX + "Choose what you'd like to do next:".center(60))
        print(Fore.MAGENTA + "═" * 50 + "💫" + Style.RESET_ALL)

        print("1. ✨ Start a new story")
        print("2. 🔁 Continue a saved story")
        print("3. 📜 View old stories")
        print("4. 📤 Export a story")
        print("5. 🗑️  Delete a story")
        print("6. 🚪 Logout")

        option = input(Fore.LIGHTGREEN_EX + "\nChoose (1-6): ").strip()

        try:
            if option == "1":
                manager.start_new_story()

            elif option == "2":
                manager.load_old_stories()

            elif option == "3":
                manager.view_old_story()

            elif option == "4":
                manager.export_story()

            elif option == "5":
                manager.delete_story()

            elif option == "6":
                print(Fore.MAGENTA + f"\n👋 Goodbye, {user.username}! Thank you for creating stories with us 🌙")
                print(Fore.MAGENTA + "💫" + "═" * 46 + "💫")
                break

            else:
                print(Fore.RED + "⚠️ Invalid option. Please choose between 1-6.")

        except RuntimeError as e:
            print(Fore.RED + f"\n⚠️ {e}")
            print(Fore.LIGHTBLUE_EX + "↩️ Returning to main menu...\n")

        except Exception as e:
            print(Fore.RED + f"\n❌ Unexpected error: {e}")
            print(Fore.LIGHTBLUE_EX + "↩️ Returning safely to main menu...\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\n\n👋 Program interrupted. Goodbye! 🌙")
