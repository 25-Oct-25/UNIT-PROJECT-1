from art import tprint
from auth import admin, login, singup
from Ai import ai_gemini
from controller import admin_controllar, cart_controller, user_controller
import time

# ANSI Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

def print_banner():
    print(CYAN)
    tprint("E - Store", font="rnd-xlarge")
    print(f"{MAGENTA}{'═' * 60}")
    print(f"{'Welcome to the Ultimate Shopping Experience!'.center(60)}")
    print(f"{'═' * 60}{RESET}\n")

def main():
    print_banner()
    while True:
        print(f"""
{YELLOW}Please choose an option:{RESET}

    {GREEN}[1]{RESET} 🧾 Sign Up
    {GREEN}[2]{RESET} 🔑 Login
    {GREEN}[3]{RESET} 🛠️  Admin Panel
    {RED}[0]{RESET} ❌ Exit
""")

        try:
            user_choice = int(input(f"{CYAN}👉 Enter your choice: {RESET}"))
        except ValueError:
            print(f"{RED}❌ Invalid input. Please enter a number.{RESET}")
            time.sleep(1.5)
            continue

        if user_choice == 0:
            print(f"{GREEN}👋 Thank you for visiting E-Store!{RESET}")
            break

        elif user_choice == 1:
            if singup.sign_up():
                log, user_email = login.login()
                if log:
                    user_menu(user_email)

        elif user_choice == 2:
            log, user_email = login.login()
            if log:
                user_menu(user_email)

        elif user_choice == 3:
            if admin.login():
                admin_menu()
        else:
            print(f"{RED}❌ Invalid choice. Try again.{RESET}")
            time.sleep(1.5)


def user_menu(user_email):
    print(CYAN)
    tprint("User Panel", font="small")
    print(f"{YELLOW}{'─' * 50}")
    print(f"{'Welcome back to your dashboard!'.center(50)}")
    print(f"{'─' * 50}{RESET}")

    while True:
        print(f"""
    {GREEN}[1]{RESET} 🛍️  Show All Products
    {GREEN}[2]{RESET} 🔍 Search Products
    {GREEN}[3]{RESET} ➕ Add Product to Cart
    {GREEN}[4]{RESET} 🗑️  Delete Product from Cart
    {GREEN}[5]{RESET} 🧺 Show My Cart
    {GREEN}[6]{RESET} 💳 Pay & Receive Invoice
    {GREEN}[7]{RESET} 🤖 Gemini Assistant
    {GREEN}[8]{RESET} 💬 Add Review For Products
    {GREEN}[9]{RESET} 🔍 Show Review For Products   
    {GREEN}[10]{RESET} 🔍 Sort Products By Rating Or Most Solds 
    {RED}[0]{RESET} 🚪 Logout
""")

        try:
            choice = int(input(f"{CYAN}👉 Enter your choice: {RESET}"))
        except ValueError:
            print(f"{RED}❌ Please enter a valid number.{RESET}")
            time.sleep(1.5)
            continue

        if choice == 0:
            print(f"{GREEN}✅ Logged out successfully!{RESET}")
            time.sleep(1)
            break
        elif choice == 1:
            user_controller.show_products()
        elif choice == 2:
            user_controller.show_products()
        elif choice == 3:
            product_name = input("🛒 Enter product name to add: ").strip()
            user_controller.add_products_to_cart(user_email, product_name)
        elif choice == 4:
            cart_controller.delete_product(user_email)
        elif choice == 5:
            cart_controller.show_cart(user_email)
        elif choice == 6:
            cart_controller.payments(user_email)
            cart_controller.products_solds(user_email)
        elif choice == 7:
            ai_gemini.chat_with_ai()
        elif choice == 8 :
            user_controller.add_reviews(user_email)
        elif choice == 9 :
            user_controller.show_product_reviews()
        elif choice == 10 :
            user_controller.sort_by_rating_or_most_sold()
        else:
            print(f"{RED}❌ Invalid choice. Try again.{RESET}")
            time.sleep(1.5)


def admin_menu():
    
    print(MAGENTA)
    tprint("Admin", font="small")
    print(f"{YELLOW}{'─' * 50}")
    print(f"{'Welcome, Administrator!'.center(50)}")
    print(f"{'─' * 50}{RESET}")

    while True:
        print(f"""
    {GREEN}[1]{RESET} ➕ Add New Product
    {GREEN}[2]{RESET} ✏️  Edit Existing Product
    {GREEN}[3]{RESET}  ➕ Add Discounts 
    {RED}[0]{RESET} 🚪 Logout
""")

        try:
            choice = int(input(f"{CYAN}👉 Enter your choice: {RESET}"))
        except ValueError:
            print(f"{RED}❌ Invalid input. Please enter a number.{RESET}")
            time.sleep(1.5)
            continue

        if choice == 0:
            print(f"{GREEN}✅ Logged out from admin panel.{RESET}")
            time.sleep(1)
            break
        elif choice == 1:
            admin_controllar.add_products()
        elif choice == 2:
            admin_controllar.edit_products()
        elif choice == 3:
            admin_controllar.add_discounts()
        else:
            print(f"{RED}❌ Invalid choice. Try again.{RESET}")
            time.sleep(1.5)


if __name__ == "__main__":
    main()
