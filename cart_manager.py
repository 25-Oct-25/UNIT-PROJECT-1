# cart_manager.py

from bookstore_data import users_db, save_data
from book_manager import get_book_price, get_book_quantity

def add_to_cart(username, book_title, quantity=1):
    """Adds a book to the user's shopping cart."""
    if username not in users_db:
        print("Error: User does not exist.")
        return False

    if get_book_quantity(book_title) is None:
        print(f"The book '{book_title}' does not exist.")
        return False

    current_in_cart = users_db[username]["cart"].get(book_title, 0)
    
    if get_book_quantity(book_title) < (quantity + current_in_cart):
        print(f"Sorry, not enough quantity of '{book_title}' available. Available: {get_book_quantity(book_title)}")
        return False

    user_cart = users_db[username]["cart"]
    if book_title in user_cart:
        user_cart[book_title] += quantity
    else:
        user_cart[book_title] = quantity
    
    save_data() # Save changes to cart
    print(f"Added {quantity} of '{book_title}' to your cart.")
    return True

def remove_from_cart(username, book_title, quantity=1):
    """Removes a book from the user's shopping cart."""
    if username not in users_db:
        print("Error: User does not exist.")
        return False

    user_cart = users_db[username]["cart"]
    if book_title not in user_cart:
        print(f"The book '{book_title}' is not in your cart.")
        return False
    
    if user_cart[book_title] <= quantity:
        del user_cart[book_title]
        print(f"'{book_title}' completely removed from your cart.")
    else:
        user_cart[book_title] -= quantity
        print(f"Removed {quantity} of '{book_title}' from your cart.")
    save_data() # Save changes
    return True

def view_cart(username):
    """Displays the contents of the user's shopping cart."""
    if username not in users_db:
        print("Error: User does not exist.")
        return 0.0

    user_cart = users_db[username]["cart"]
    if not user_cart:
        print("Your cart is empty.")
        return 0.0

    print("\n--- Your Shopping Cart ---")
    total_price = 0.0
    for book_title, quantity in user_cart.items():
        price = get_book_price(book_title)
        if price:
            item_total = price * quantity
            total_price += item_total
            print(f"- {book_title} (x{quantity}) - ${price:.2f} per book = ${item_total:.2f}")
        else:
            print(f"- {book_title} (x{quantity}) - Price not available (book might not exist)")
    print(f"--------------------------")
    print(f"Cart Total: ${total_price:.2f}")
    return total_price

def clear_cart(username):
    """Clears the user's shopping cart."""
    if username in users_db:
        users_db[username]["cart"] = {}
        save_data() # Save changes
        return True
    return False