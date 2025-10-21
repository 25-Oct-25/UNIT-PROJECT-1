from User import User
from StoryManager import StoryManager

def main():
    print("\n=== Interactive Story App ===")
    print("1. Login")
    print("2. Sign Up")
    choice = input("Choose (1/2): ").strip()

    user = None
    #handel user choice for login or signup
    if choice == "1":
        user = User.login()
    elif choice == "2":
        user = User.signup()
    else:
        print("Invalid choice.")
        return

    # if user successfully logged in or sighn up
    if user:
        print(f"\nWelcome, {user.username}!")
        manager = StoryManager(user.username)

        # resume last unfinished story
        print("\nChecking if you have a previous story...")
        manager.resume_last_story()

        while True:
            print("\n=== Story Menu ===")
            print("1. Start a new story")
            print("2. Continue a story")
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
                print(f"Goodbye, {user.username}!")
                break
            else:
                print(" Invalid option. Try again.")
    else:
        print(" Login or signup failed. Try again.")

if __name__ == "__main__":
    main()
