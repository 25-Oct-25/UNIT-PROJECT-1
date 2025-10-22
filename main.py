from User import User
from StoryManager import StoryManager


def main():
    """Main entry point of the Interactive Story App."""
    print("\n=== 🌙 Welcome to the AI Interactive Story Creator ===")
    print("------------------------------------------------------")

    user = None

    # Authentication loop
    while not user:
        print("\n1. Login")
        print("2. Sign Up")
        print("3. Exit")

        choice = input("Choose (1/2/3): ").strip()

        if choice == "1":
            user = User.login()
            if not user:
                retry = input("\n❌ Login failed. Try again? (y/n): ").strip().lower()
                if retry == "n":
                    print("\nWould you like to sign up for a new account?")
                    signup_choice = input("Sign up now? (y/n): ").strip().lower()
                    if signup_choice == "y":
                        user = User.signup()
                    else:
                        print("Goodbye!")
                        return
        elif choice == "2":
            user = User.signup()
        elif choice == "3":
            print("Goodbye 👋")
            return
        else:
            print("⚠️ Invalid option. Please choose 1, 2, or 3.")

    # If user logged in or signed up successfully
    #print(f"\n✅ Welcome, {user.username}!")
    manager = StoryManager(user.username)

    # Check if there is a previously saved story
    print("\nChecking if you have a previous story...")
    manager.resume_last_story()

    # Main story menu loop
    while True:
        print("\n=== 📚 Story Menu ===")
        print("1. Start a new story")
        print("2. Continue a saved story")
        print("3. View old stories")
        print("4. Export a story")
        print("5. Exit")

        option = input("Choose (1-5): ").strip()

        if option == "1":
            manager.start_new_story()
        elif option == "2":
            manager.load_old_stories()
        elif option == "3":
            manager.view_old_story()
        elif option == "4":
            manager.export_story()
        elif option == "5":
            print(f"\n👋 Goodbye, {user.username}! Thanks for creating stories with us.")
            break
        else:
            print("⚠️ Invalid option. Please choose between 1-5.")


if __name__ == "__main__":
    main()
