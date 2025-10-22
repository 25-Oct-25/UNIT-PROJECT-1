# admin_panel.py

from bookstore_data import books_db, orders_db, users_db, low_stock_threshold, save_data
from book_manager import add_book, remove_book, get_book_details

def admin_add_book_prompt():
    """Prompts the admin to add a new book."""
    print("\n--- Add New Book ---")
    title = input("Enter book title: ")
    author = input("Enter author name: ")
    description = input("Enter book description: ")
    genre = input("Enter book genre (e.g., Fantasy, Romance, Dystopian): ")
    try:
        price = float(input("Enter book price: "))
        quantity = int(input("Enter initial quantity: "))
    except ValueError:
        print("Error: Price and quantity must be numbers.")
        return
    isbn = input("Enter ISBN: ")
    add_book(title, author, description, price, quantity, isbn, genre)

def admin_remove_book_prompt():
    """Prompts the admin to remove a book."""
    print("\n--- Remove Book ---")
    title = input("Enter the title of the book to remove: ")
    remove_book(title)

def admin_view_all_orders():
    """Displays all orders in the system."""
    if not orders_db:
        print("No orders currently in the system.")
        return

    print("\n--- All Orders in System ---")
    for order_id, order_details in orders_db.items():
        print(f"\nOrder ID: {order_id}")
        print(f"  Username: {order_details['username']}")
        print(f"  Total Amount: ${order_details['total_amount']:.2f}")
        print(f"  Status: {order_details['status']}")
        print(f"  Order Date: {order_details['order_date']}")
        print(f"  Shipping Address: {order_details['shipping_address']['street']}, {order_details['shipping_address']['city']}")
        print("  Items:")
        for item_title, item_qty in order_details['items'].items():
            print(f"    - {item_title} (x{item_qty})")
    print("----------------------------")

def admin_update_order_status():
    """Allows the admin to update the status of an order."""
    order_id = input("Enter the Order ID to update its status: ")
    if order_id not in orders_db:
        print(f"Order '{order_id}' not found.")
        return

    print(f"Current status for Order '{order_id}': {orders_db[order_id]['status']}")
    new_status = input("Enter the new status (e.g., 'Shipped', 'Delivered', 'Cancelled'): ")
    orders_db[order_id]['status'] = new_status
    save_data() # Save changes
    print(f"Order '{order_id}' status updated to '{new_status}' successfully.")

def admin_view_all_users():
    """Displays a list of all registered users."""
    if not users_db:
        print("No users registered yet.")
        return

    print("\n--- All Registered Users ---")
    for username, data in users_db.items():
        is_admin_str = "(Admin)" if data.get("is_admin", False) else ""
        print(f"- {username} {is_admin_str}")
        print(f"  Email: {data.get('email', 'N/A')}")
        if data.get("purchase_history"):
            print(f"  Purchase History: {len(data['purchase_history'])} orders")
        if data.get("address"):
            addr = data['address']
            print(f"  Address: {addr.get('street', '')}, {addr.get('city', '')}")
    print("----------------------------")

def check_low_stock_alerts():
    """Checks for low stock books and prints alerts."""
    low_stock_books = []
    for title, data in books_db.items():
        if data['quantity'] <= low_stock_threshold:
            low_stock_books.append((title, data['quantity']))
    
    if low_stock_books:
        print("\n!!! LOW STOCK ALERT !!!")
        for title, quantity in low_stock_books:
            print(f"- Book '{title}' has low stock: {quantity} remaining.")
        print("Please restock these books soon.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return True
    else:
        print("No books currently with low stock.")
        return False