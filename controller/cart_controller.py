import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ======= FILE PATHS =======
cart_path = "C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/carts.json"
user_path = "C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/users.json"
products_most_solds = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/products_most_sold.json'
discounts_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/discounts.json'


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# ======= HELPER FUNCTION =======
def get_user_id(user_email: str) -> int:
    
    """Return the user's ID based on their email."""
    
    try:
        with open(user_path, 'r', encoding='utf-8') as file:
            users = json.load(file)
    except FileNotFoundError:
        print("User file not found.")
        return None

    for user in users:
        if user_email == user['email']:
            return user['id']

    print("User not found.")
    return None


# ======= CART TOTAL =======
def cart_total_price(user_email: str) -> float:
    """Calculate the total price of all products in the user's cart (supports quantity)."""

    user_id = get_user_id(user_email)
    if user_id is None:
        return 0

    try:
        with open(cart_path, 'r', encoding='utf-8') as file:
            carts = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ Cart file not found or empty.")
        return 0

    total = 0.0

    for cart in carts:
        if cart['user_id'] == user_id:
            for item in cart['cart']:
                price = float(item.get('product_price', 0))
                quantity = int(item.get('product_quantity', 1)) 
                total += price * quantity

    print(f"🧾 Total price: ${total:.2f}")
    return total


# ======= SHOW CART =======
def show_cart(user_email: str) -> None:
    
    """Display all products in the user's cart."""
    
    user_id = get_user_id(user_email)
    if user_id is None:
        return

    try:
        with open(cart_path, 'r', encoding='utf-8') as file:
            carts = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Cart file not found or empty.")
        return

    found = False
    for cart in carts:
        if cart['user_id'] == user_id:
            found = True
            print("\n------ Your Cart ------")
            for item in cart['cart']:
                print(f"Category: {item['product_category']}")
                print(f"Product Name: {item['product_name']}")
                print(f"Product Quantity: {item['product_quantity']}")
                print(f"Price: ${item['total_price']}")
                print("--------------------------")
            break

    if not found:
        print("Cart is empty for this user.")


# ======= DELETE PRODUCT =======
def delete_product(user_email: str) -> bool:
    
    """Delete a product from the user's cart."""
    
    product_name = input("Enter the product name to delete: ").strip()

    user_id = get_user_id(user_email)
    if not user_id:
        print("User not found.")
        return False

    try:
        with open(cart_path, 'r', encoding='utf-8') as file:
            carts = json.load(file)
    except FileNotFoundError:
        print("Cart file not found.")
        return False

    for cart in carts:
        if cart['user_id'] == user_id:
            for item in cart['cart']:
                if item['product_name'].lower() == product_name.lower():
                    cart['cart'].remove(item)
                    with open(cart_path, 'w', encoding='utf-8') as file:
                        json.dump(carts, file, indent=4, ensure_ascii=False)
                    print(f"'{product_name}' deleted successfully from cart.")
                    return True
            print("Product not found in your cart.")
            return False

    print("Cart not found for this user.")
    return False


# ======= DISCOUNTS =======
def load_discounts() -> dict:
    """Loads discount codes and rates from the JSON file."""
    try:
        with open(discounts_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return an empty dictionary if the file is missing or empty
        return {}
    

# ======= PAYMENTS =======
def payments(user_email: str) -> bool:
    """Generate a PDF invoice for the user's cart and send it via email."""

    user_id = get_user_id(user_email)
    if not user_id:
        print("User not found.")
        return False

    try:
        with open(cart_path, 'r', encoding='utf-8') as file:
            carts = json.load(file)
    except FileNotFoundError:
        print("Cart file not found.")
        return False

    user_cart = None
    for cart in carts:
        if cart['user_id'] == user_id:
            user_cart = cart['cart']
            break

    if not user_cart:
        print("Cart is empty.")
        return False

    total_price = cart_total_price(user_email)
    discount_rate = 0.0
    discount_amount = 0.0

    print(f"\nYour current total is: ${total_price:.2f}")
    coupon_code = input("Enter discount code (or press Enter to skip): ").strip().upper()

    if coupon_code:
        discounts = load_discounts()
        if coupon_code in discounts:
            discount_rate = discounts[coupon_code]
            discount_amount = total_price * discount_rate
            total_price -= discount_amount 
            print(f"🎉 Discount '{coupon_code}' applied successfully!")
            print(f"Discount amount: -${discount_amount:.2f} ({discount_rate*100:.0f}%)")
        else:
            print("❌ Invalid discount code. Proceeding without discount.")

    # Create directory for invoices
    os.makedirs("EMAILS_PDF/invoices", exist_ok=True)

    # Create PDF
    pdf_path = f"EMAILS_PDF/invoices/{user_email}_invoice.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # ===== HEADER =====
    c.setFont("Helvetica-Bold", 18)
    c.drawString(230, height - 80, "INVOICE")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 120, f"User Email: {user_email}")
    c.drawString(50, height - 140, f"User ID: {user_id}")
    c.line(50, height - 150, 550, height - 150)

    # ===== TABLE HEADER =====
    y = height - 180
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Product Name")
    c.drawString(250, y, "Category")
    c.drawString(380, y, "Qty")
    c.drawString(430, y, "Price ($)")
    c.drawString(510, y, "Total ($)")
    y -= 20

    # ===== PRODUCT ROWS =====
    c.setFont("Helvetica", 11)
    for item in user_cart:
        qty = int(item.get('product_quantity', 1))
        price = float(item['product_price'])
        total_item = qty * price

        c.drawString(50, y, item['product_name'])
        c.drawString(250, y, item['product_category'])
        c.drawString(385, y, str(qty))
        c.drawString(435, y, f"{price:.2f}")
        c.drawString(515, y, f"{total_item:.2f}")
        y -= 20

        if y < 100:  # if page is full, go to next page
            c.showPage()
            y = height - 100

    # ===== TOTAL =====
    c.line(50, y - 10, 550, y - 10)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(400, y - 30, f"Subtotal: ${total_price + discount_amount:.2f}")

    # Displaying Discount (if any)
    if discount_amount > 0:
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.red)
        c.drawString(400, y - 50, f"Discount ({coupon_code}): -${discount_amount:.2f}")
        c.setFillColor(colors.black)
        c.line(400, y - 65, 550, y - 65)
        y -= 20
    
    # Displaying Grand Total (Final Price)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, y - 70, f"Grand Total: ${total_price:.2f}")
    y -= 40 # Adjust y for the footer

    return send_email(user_email, pdf_path, total_price)


# ======= SEND EMAIL =======
def send_email(user_email: str, pdf_path: str,final_price:float) -> bool:
    
    """Send invoice as an email attachment."""
    
    try:
        msg = MIMEMultipart()
        msg["Subject"] = "Your Invoice - E-Store"
        msg["From"] = "alhrbiabdulrahman3@gmail.com"
        msg["To"] = user_email

        body = f"""
        Dear {user_email},
        
        Thank you for shopping at E-Store!
        Your invoice is attached as a PDF.
        
        Total: ${final_price:.2f}
        
        Best regards,
        E-Store Team
        """
        msg.attach(MIMEText(body, "plain"))

        with open(pdf_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(pdf_path)}",
        )
        msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # App password 
        server.send_message(msg)
        server.quit()

        print(f"Invoice sent successfully to {user_email}")
        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    

# ======= How many products solds =======
def products_solds(user_email) -> None:

    user_id = get_user_id(user_email)

    try:
        with open(cart_path, 'r', encoding='utf-8') as file:
            carts = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    user_cart = None
    for cart in carts:
        if cart['user_id'] == user_id:
            user_cart = cart['cart']
            break

    if not user_cart:
        return

    items = [item['product_name'] for item in user_cart]

    try:
        with open(products_most_solds, 'r', encoding='utf-8') as file:
            products = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        products = []

    product_dict = {p['product_name']: p['number_of_solds'] for p in products}

    for name in items:
        if name in product_dict:
            product_dict[name] += 1
        else:
            product_dict[name] = 1

    updated_products = [
        {'product_name': k, 'number_of_solds': v} for k, v in product_dict.items()
    ]

    with open(products_most_solds, 'w', encoding='utf-8') as file:
        json.dump(updated_products, file, indent=4, ensure_ascii=False)

