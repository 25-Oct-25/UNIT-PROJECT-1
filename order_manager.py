# order_manager.py

import uuid
from datetime import datetime
import smtplib # Import SMTP library for email sending
from email.mime.text import MIMEText # For MIME text format
from email.mime.multipart import MIMEMultipart # For multi-part content

from bookstore_data import users_db, orders_db, save_data
from cart_manager import view_cart, clear_cart
from user_manager import get_shipping_address, get_user_email
from book_manager import update_book_quantity, get_book_price

# =========================================================================
# EMAIL INFORMATION - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
# =========================================================================
SENDER_EMAIL = "your_email@gmail.com"  # Replace with your email address
SENDER_PASSWORD = "your_app_password"  # Replace with your Gmail App Password
# =========================================================================

def generate_receipt_content(order_id):
    """Generates receipt content as a string for email/display."""
    order = orders_db.get(order_id)
    if not order:
        return "Error: Order not found."

    content = f"Dear {order['username']},\n"
    content += f"Thank you for your order from our bookstore! Your order details are as follows:\n\n"
    content += f"--- Your Bookstore Order Receipt ---\n"
    content += f"Order ID: {order_id}\n"
    content += f"Order Date: {order['order_date']}\n"
    content += f"Shipping Address: {order['shipping_address']['street']}, {order['shipping_address']['city']}, {order['shipping_address']['state']} {order['shipping_address']['zip_code']}\n"
    content += f"\nItems:\n"
    for book_title, quantity in order['items'].items():
        price = get_book_price(book_title) or 0.0
        item_total = price * quantity
        content += f"  - {book_title} (x{quantity}) - ${price:.2f} each = ${item_total:.2f}\n"
    content += f"\nTotal Amount: ${order['total_amount']:.2f}\n"
    content += f"Status: {order['status']}\n"
    content += f"\nThank you for shopping with us!\n"
    content += f"The Bookstore Team\n"
    content += f"-----------------------------------\n"
    return content

def send_email_receipt(recipient_email, order_id):
    """Sends a real email receipt."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("\nEmail setup error: Please configure SENDER_EMAIL and SENDER_PASSWORD in order_manager.py.")
        print("If using Gmail with 2-Factor Authentication, use an App Password.")
        return False

    if not recipient_email:
        print("Recipient email address is not available.")
        return False

    receipt_body = generate_receipt_content(order_id)
    subject = f"Your Bookstore Order Receipt #{order_id}"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Attach plain text message, specify utf-8 for proper character encoding (Arabic, etc.)
    msg.attach(MIMEText(receipt_body, 'plain', 'utf-8'))

    try:
        # Use SSL for secure connection
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.close()
        print(f"\nOrder receipt #{order_id} successfully sent to {recipient_email}!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("\nSMTP Authentication Error: Check your email and App Password.")
        print("Ensure you're using an App Password if 2-Step Verification is enabled for Gmail.")
        return False
    except Exception as e:
        print(f"\nAn error occurred while sending email: {e}")
        return False

def checkout(username):
    """Performs the checkout process for the user."""
    if username not in users_db:
        print("Error: User does not exist.")
        return False

    user_cart = users_db[username]["cart"]
    if not user_cart:
        print("Your cart is empty. Cannot proceed to checkout.")
        return False

    address = get_shipping_address(username)
    if not address:
        print("Please set your shipping address first before checking out.")
        return False

    recipient_email = get_user_email(username)
    if not recipient_email:
        print("Sorry, no email address registered for this user.")
        print("Please update your information or register with a valid email.")
        return False

    print("\n--- Order Summary ---")
    total_amount = view_cart(username)
    if total_amount == 0.0:
        return False

    print(f"  Shipping Address: {address['street']}, {address['city']}, {address['state']} {address['zip_code']}")
    print(f"  Total Amount: ${total_amount:.2f}")
    print(f"  Receipt will be sent to: {recipient_email}")

    confirm = input("Are you sure you want to proceed with checkout? (yes/no): ").lower()
    if confirm != 'yes':
        print("Checkout cancelled.")
        return False

    # Re-check stock availability before finalizing the order
    for book_title, quantity in user_cart.items():
        if not update_book_quantity(book_title, -quantity):
            print(f"Sorry, not enough quantity of '{book_title}' available to complete your order.")
            # In a real system, you'd need to roll back any previous quantity updates here
            return False

    order_id = str(uuid.uuid4())
    order_details = {
        "username": username,
        "items": dict(user_cart),
        "total_amount": total_amount,
        "shipping_address": address,
        "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Processing"
    }
    orders_db[order_id] = order_details
    users_db[username]["purchase_history"].append(order_id)
    
    clear_cart(username)
    save_data() # Save changes after checkout

    print(f"\nCheckout successful! Your order ID is: {order_id}")
    
    # Send actual email receipt
    send_email_receipt(recipient_email, order_id)

    print_receipt(order_id) # Display receipt in CLI
    return True

def print_receipt(order_id):
    """Prints a receipt for a specific order."""
    print(generate_receipt_content(order_id))
    return True

def check_delivery_status(order_id):
    """Checks the delivery status of a specific order."""
    order = orders_db.get(order_id)
    if order:
        print(f"\n--- Delivery Status for Order: {order_id} ---")
        print(f"  Status: {order['status']}")
        print(f"  Order Date: {order['order_date']}")
        print(f"  Shipping Address: {order['shipping_address']['street']}, {order['shipping_address']['city']}, {order['shipping_address']['state']} {order['shipping_address']['zip_code']}")
        print("---------------------------------")
        return True
    else:
        print(f"Order '{order_id}' not found.")
        return False

def get_recommendations(username):
    """
    Provides recommendations based on purchase history (simplified: recommends books not yet purchased).
    """
    if username not in users_db:
        print("Error: User does not exist.")
        return

    purchase_history = users_db[username]["purchase_history"]
    purchased_book_titles = set()
    purchased_genres = set()
    for order_id in purchase_history:
        order = orders_db.get(order_id)
        if order:
            for book_title in order['items'].keys():
                purchased_book_titles.add(book_title)
                from bookstore_data import books_db
                book_data = books_db.get(book_title)
                if book_data and book_data.get('genre'):
                    purchased_genres.add(book_data['genre'])

    from bookstore_data import books_db
    all_book_titles = set(books_db.keys())

    recommended_books = []
    # First, recommend books from preferred genres
    for title, data in books_db.items():
        if title not in purchased_book_titles and data.get('genre') in purchased_genres:
            recommended_books.append(title)
    
    # If no genre-based recommendations, recommend books not yet purchased
    if not recommended_books:
        recommended_books = list(all_book_titles - purchased_book_titles)

    if not recommended_books:
        print("No new recommendations available (maybe you've bought all our books!).")
        return

    print("\n--- Recommendations for You Based on Past Purchases ---")
    for book_title in recommended_books:
        book_data = books_db.get(book_title)
        avg_rating = 0
        if book_data and book_data['reviews']:
            total_rating = sum(review['rating'] for review in book_data['reviews'])
            avg_rating = total_rating / len(book_data['reviews'])
        rating_str = f" (Rating: {avg_rating:.1f}/5)" if avg_rating > 0 else ""
        print(f"- {book_title} by {book_data['author']} (Genre: {book_data.get('genre', 'N/A')}){rating_str}")
    print("---------------------------------------------------")