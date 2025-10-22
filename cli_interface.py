# cli_interface.py

import sys
from user_manager import register_user, login_user, set_shipping_address, is_admin
from book_manager import list_all_books, get_book_details, search_books, add_book_review, filter_books_by_genre, get_available_genres
from cart_manager import add_to_cart, remove_from_cart, view_cart
from order_manager import checkout, check_delivery_status, get_recommendations
from admin_panel import admin_add_book_prompt, admin_remove_book_prompt, admin_view_all_orders, admin_update_order_status, admin_view_all_users, check_low_stock_alerts
from bookstore_data import save_data # Ensure data is saved on exit

current_user = None

def display_customer_menu():
    print("\n--- Customer Menu ---")
    print("1. Browse All Books (list_books)")
    print("2. View Book Details (show <book_name>)")
    print("3. Search for Books (search <query>)")
    print("4. Filter Books by Genre (filter_by_genre <genre_name>)")
    print("5. Add Book to Cart (add_to_cart <book_name> [quantity])")
    print("6. Remove Book from Cart (remove_from_cart <book_name> [quantity])")
    print("7. View Shopping Cart (view_cart)")
    print("8. Set Shipping Address (set_address)")
    print("9. Checkout (checkout)")
    print("10. Check Delivery Status (check_status <order_id>)")
    print("11. Get Recommendations (recommendations)")
    print("12. Add Book Review (review_book <book_name>)")
    print("13. Logout (logout)")
    print("14. Exit Application (exit)")
    print("---------------------")

def display_admin_menu():
    print("\n--- Admin Menu ---")
    print("1. Browse All Books (list_books)")
    print("2. View Book Details (show <book_name>)")
    print("3. Add New Book (admin_add_book)")
    print("4. Remove Book (admin_remove_book)")
    print("5. View All Orders (admin_view_orders)")
    print("6. Update Order Status (admin_update_order_status)")
    print("7. View All Users (admin_view_users)")
    print("8. Check Low Stock Alerts (check_low_stock)")
    print("9. Logout (logout)")
    print("10. Exit Application (exit)")
    print("------------------")

def handle_customer_commands(command_parts):
    global current_user
    cmd = command_parts[0]

    if cmd == "list_books":
        list_all_books()
    elif cmd == "show":
        if len(command_parts) < 2:
            print("Usage: show <book_name>")
            return
        book_title = " ".join(command_parts[1:])
        get_book_details(book_title)
    elif cmd == "search":
        if len(command_parts) < 2:
            print("Usage: search <query>")
            return
        query = " ".join(command_parts[1:])
        search_books(query)
    elif cmd == "filter_by_genre":
        if len(command_parts) < 2:
            print("Usage: filter_by_genre <genre_name>")
            print("Available Genres: " + ", ".join(get_available_genres()))
            return
        genre_name = " ".join(command_parts[1:])
        filter_books_by_genre(genre_name)
    elif cmd == "add_to_cart":
        if len(command_parts) < 2:
            print("Usage: add_to_cart <book_name> [quantity]")
            return
        # Determine quantity if provided as a number at the end of the command
        quantity_str = command_parts[-1]
        if quantity_str.isdigit() and len(command_parts) > 2:
            quantity = int(quantity_str)
            book_title = " ".join(command_parts[1:-1])
        else:
            quantity = 1
            book_title = " ".join(command_parts[1:])
        add_to_cart(current_user, book_title, quantity)
    elif cmd == "remove_from_cart":
        if len(command_parts) < 2:
            print("Usage: remove_from_cart <book_name> [quantity]")
            return
        quantity_str = command_parts[-1]
        if quantity_str.isdigit() and len(command_parts) > 2:
            quantity = int(quantity_str)
            book_title = " ".join(command_parts[1:-1])
        else:
            quantity = 1
            book_title = " ".join(command_parts[1:])
        remove_from_cart(current_user, book_title, quantity)
    elif cmd == "view_cart":
        view_cart(current_user)
    elif cmd == "set_address":
        print("Enter your shipping address details:")
        street = input("Street and Building Number: ")
        city = input("City: ")
        state = input("State/Province: ")
        zip_code = input("Zip Code: ")
        set_shipping_address(current_user, street, city, state, zip_code)
    elif cmd == "checkout":
        checkout(current_user)
    elif cmd == "check_status":
        if len(command_parts) < 2:
            print("Usage: check_status <order_id>")
            return
        order_id = command_parts[1]
        check_delivery_status(order_id)
    elif cmd == "recommendations":
        get_recommendations(current_user)
    elif cmd == "review_book":
        if len(command_parts) < 2:
            print("Usage: review_book <book_name>")
            return
        book_title = " ".join(command_parts[1:])
        rating = input(f"Enter your rating for '{book_title}' (1 to 5): ")
        comment = input("Enter your comment (optional, press Enter to skip): ")
        add_book_review(current_user, book_title, rating, comment if comment else "No comment.")
    elif cmd == "logout":
        current_user = None
        print("Logged out successfully.")
    elif cmd == "exit":
        save_data() # Save data before exiting
        print("Thank you for using the Online Bookstore. Goodbye!")
        sys.exit()
    else:
        print("Invalid command. Please check the menu.")

def handle_admin_commands(command_parts):
    global current_user
    cmd = command_parts[0]

    if cmd == "list_books":
        list_all_books()
    elif cmd == "show":
        if len(command_parts) < 2:
            print("Usage: show <book_name>")
            return
        book_title = " ".join(command_parts[1:])
        get_book_details(book_title)
    elif cmd == "admin_add_book":
        admin_add_book_prompt()
    elif cmd == "admin_remove_book":
        admin_remove_book_prompt()
    elif cmd == "admin_view_orders":
        admin_view_all_orders()
    elif cmd == "admin_update_order_status":
        admin_update_order_status()
    elif cmd == "admin_view_users":
        admin_view_all_users()
    elif cmd == "check_low_stock":
        check_low_stock_alerts()
    elif cmd == "logout":
        current_user = None
        print("Logged out successfully.")
    elif cmd == "exit":
        save_data() # Save data before exiting
        print("Thank you for using the Online Bookstore. Goodbye!")
        sys.exit()
    else:
        print("Invalid command. Please check the menu.")

def main_menu():
    print("\n--- Welcome to the Online Bookstore! ---")
    print("1. Login (login)")
    print("2. Register (register)")
    print("3. Exit (exit)")
    print("--------------------------------------")

def run_cli():
    global current_user

    while True:
        if current_user is None:
            main_menu()
            choice = input("Enter your option (login/register/exit): ").lower()
            if choice == "login":
                username = input("Username: ")
                password = input("Password: ")
                if login_user(username, password):
                    current_user = username
            elif choice == "register":
                username = input("New Username: ")
                password = input("Password: ")
                email = input("Email Address: ") # Request email
                register_user(username, password, email)
            elif choice == "exit":
                save_data() # Save data before exiting
                print("Thank you for using the Online Bookstore. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")
        else:
            if is_admin(current_user):
                display_admin_menu()
                command = input(f"{current_user} (Admin) > ").strip()
                if not command:
                    continue # Ignore empty command

                command_parts = command.split(' ', 1)
                command_parts[0] = command_parts[0].lower() # Only the main command is lowercase

                if command_parts[0] == "exit":
                    save_data() # Save data before exiting
                    print("Thank you for using the Online Bookstore. Goodbye!")
                    sys.exit()
                elif command_parts[0] == "logout":
                    current_user = None
                    print("Logged out successfully.")
                else:
                    handle_admin_commands(command_parts)
            else:
                display_customer_menu()
                command = input(f"{current_user} > ").strip()
                if not command:
                    continue # Ignore empty command

                command_parts = command.split(' ', 1)
                command_parts[0] = command_parts[0].lower() # Only the main command is lowercase

                if command_parts[0] == "exit":
                    save_data() # Save data before exiting
                    print("Thank you for using the Online Bookstore. Goodbye!")
                    sys.exit()
                elif command_parts[0] == "logout":
                    current_user = None
                    print("Logged out successfully.")
                else:
                    handle_customer_commands(command_parts)

if __name__ == "__main__":
    run_cli()