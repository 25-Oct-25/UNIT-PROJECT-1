import sys
sys.stdout.reconfigure(encoding='utf-8')

from modules import auth

def main():
    print("=== Welcome to Smart Travel Assistant 🌍 ===\n")

    while True:
        print("1. Login")
        print("2. Register")
        print("3. Forgot Password")
        print("4. Exit")
        choice = input(">> ")

        if choice == "1":
            user = auth.login()
            if user:
                print(f"🎉 Welcome {user['username']}! (Flight system coming soon)")
        elif choice == "2":
            auth.register()
        elif choice == "3":
            auth.forgot_password()
        elif choice == "4":
            print("👋 Thanks for using Smart Travel Assistant.")
            break
        else:
            print("❌ Invalid choice, please try again.")

if __name__ == "__main__":
    main()
