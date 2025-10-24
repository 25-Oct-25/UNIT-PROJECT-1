from colorama import Fore, Style, init
from src.User import User
from src.StoryManager import StoryManager

# ✅ Enable colors for all terminal types
init(autoreset=True, convert=True)

def main():
    """Main entry point of the Interactive Story App."""
    print(Fore.CYAN + "\n=== 🌙 Welcome to the " + Fore.MAGENTA + "AI Interactive Story Creator "+Fore.CYAN+"===")
    print(Fore.LIGHTBLUE_EX + "------------------------------------------------------" + Style.RESET_ALL)

    user = None

    #  Authentication loop
    while not user:
        print("\n1. Login")
        print("2. Sign Up")
        print("3. Exit" + Style.RESET_ALL)

        choice = input(Fore.LIGHTGREEN_EX + "Choose (1/2/3): ").strip()

        if choice == "1":
            user = User.login()
            if not user:
                print(Fore.RED + "\n❌ Login failed.")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry == "n":
                    print(Fore.CYAN + "\nWould you like to sign up for a new account?")
                    signup_choice = input("Sign up now? (y/n): ").strip().lower()
                    if signup_choice == "y":
                        user = User.signup()
                    else:
                        print(Fore.MAGENTA + "👋 Goodbye!")
                        return
        elif choice == "2":
            user = User.signup()
        elif choice == "3":
            print(Fore.MAGENTA + "👋 Goodbye!")
            return
        else:
            print(Fore.RED + "⚠️ Invalid option. Please choose 1, 2, or 3.")

    # Successfully logged in or signed up
    manager = StoryManager(user.username)

    # 🔍Check if there is a previously saved story
    print(Fore.CYAN + "\n🔎 Checking if you have a previous story...")
    manager.resume_last_story()

    #  Main story menu loop
    while True:
        print(Fore.CYAN + "\n=== 📚 Story Menu ===" + Style.RESET_ALL)
        print("1. Start a new story")
        print("2. Continue a saved story")
        print("3. View old stories")
        print("4. Export a story")
        print("5. Delete a story")
        print("6. Logout")

        option = input(Fore.LIGHTGREEN_EX + "Choose (1-6): ").strip()

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
            print(Fore.MAGENTA + f"\n👋 Goodbye, {user.username}! Thanks for creating stories with us 🌙")
            break
        else:
            print(Fore.RED + "⚠️ Invalid option. Please choose between 1-6.")

if __name__ == "__main__":
    main()
