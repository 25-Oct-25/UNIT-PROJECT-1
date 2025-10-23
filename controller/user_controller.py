import json
from colorama import Fore, Style, init
from art import text2art

init(autoreset=True)

product_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/products.json'
cart_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/carts.json'
user_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/users.json'
reviews_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/comments_ratings.json'
products_most_solds = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/products_most_sold.json'


# ======= ADD PRODUCTS TO CART FUNCTION =======
def add_products_to_cart(user_email: str, product_name: str) -> bool:

    # Load users
    try:
        with open(user_path, 'r', encoding='utf-8') as file:
            users = json.load(file)
    except FileNotFoundError:
        print("⚠️ User file not found.")
        return False

    # Get user id by email
    user_id = next((u['id'] for u in users if u['email'] == user_email), None)
    if not user_id:
        print("⚠️ User not found.")
        return False

    # Load products
    try:
        with open(product_path, 'r', encoding='utf-8') as file:
            products = json.load(file)
    except FileNotFoundError:
        print("⚠️ Products file not found.")
        return False

    # Find product info
    product_info = next((p for p in products if p['product_name'] == product_name), None)
    if not product_info:
        print("⚠️ Product not found.")
        return False

    # Ask for quantity
    try:
        quantity = int(input(f"🛒 How many '{product_name}' would you like to add? "))
        if quantity <= 0:
            print("⚠️ Quantity must be at least 1.")
            return False
    except ValueError:
        print("⚠️ Please enter a valid number.")
        return False

    # Load or create carts
    try:
        with open(cart_path, 'r', encoding='utf-8') as file:
            carts = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        carts = []

    # Find user's cart
    user_cart = next((c for c in carts if c['user_id'] == user_id), None)

    cart_item = {
        'product_category': product_info['category'],
        'product_name': product_info['product_name'],
        'product_price': product_info['product_price'],
        'product_quantity': quantity,
        'total_price': product_info['product_price'] * quantity
    }

    # If user already has a cart
    if user_cart:
        user_cart['cart'].append(cart_item)
    else:
        carts.append({
            'user_id': user_id,
            'cart': [cart_item]
        })

    # Save cart file
    with open(cart_path, 'w', encoding='utf-8') as file:
        json.dump(carts, file, indent=4, ensure_ascii=False)

    print(f"✅ {quantity} x {product_name} added to your cart successfully.")
    return True


# ======= SHOW ALL PRODUCT FUNCTION =======
def show_products() -> None:
    print(Fore.CYAN + text2art("Products", font="small"))
    try:
        with open(product_path, "r", encoding="utf-8") as file:
            products = json.load(file)
            if not products:
                print(Fore.YELLOW + "⚠️  No products found.")
                return
    except FileNotFoundError:
        print(Fore.RED + "❌ No product file found.")
        return

    print(Fore.GREEN + "=" * 40)
    for product in products:
        print(Fore.MAGENTA + f"📦 Category : {product['category']}")
        print(Fore.CYAN + f"🛍️  Name     : {product['product_name']}")
        print(Fore.YELLOW + f"💰 Price    : {product['product_price']} SAR")
        print(Fore.GREEN + "-" * 40)
    print(Style.RESET_ALL)


# ======= SEARCH BY PRODUCT NAME FUNCTION =======
def search_by_name() -> None:
    print(Fore.CYAN + text2art("Search", font="small"))
    try:
        with open(product_path, "r", encoding="utf-8") as file:
            products = json.load(file)
            if not products:
                print(Fore.YELLOW + "⚠️  No products found.")
                return
    except FileNotFoundError:
        print(Fore.RED + "❌ No product file found.")
        return

    search_name = input(Fore.WHITE + "🔎 Enter product name: ").strip().lower()
    found = False

    print(Fore.GREEN + "\nSearching...\n")
    for product in products:
        if product["product_name"].lower() == search_name:
            print(Fore.GREEN + "=" * 40)
            print(Fore.MAGENTA + f"📦 Category : {product['category']}")
            print(Fore.CYAN + f"🛍️  Name     : {product['product_name']}")
            print(Fore.YELLOW + f"💰 Price    : {product['product_price']} SAR")
            print(Fore.GREEN + "=" * 40)
            found = True
            break

    if not found:
        print(Fore.RED + "❌ Product not found. Please check the name again.")
    print(Style.RESET_ALL)


# ======= ADD REVIWES FOR PRODUCT FUNCTION =======
def add_reviews (user_email) -> bool :

    try :
        with open(product_path,'r',encoding='utf-8') as f :
            products = json.load(f)
    except FileNotFoundError :
        print("Ther is no products found")

    product_name = str(input("Enter the product you want to review : "))

    found = False

    for product in products :
        db_product = product["product_name"]
        if  db_product == product_name :
            found = True


    comment = str(input("Enter your comment : "))
    rating = float(input("Enter your rating out of 5 : "))

    if rating > 5 :
        print("Error : rating must be 5 or less")
        return False
    
    if not found : 
        print(f"Ther is no product like : {product_name}")
        return False

    try :    
        with open (reviews_path,'r',encoding='utf-8') as file :
            reviews = json.load(file)
    except FileNotFoundError :
        reviews = []

    user_id = get_user_id(user_email)

    new_review = {
        'user_id': user_id,
        'product_name': product_name,  # Assign the string variable directly
        'review': {                    # Add a new key for the review details
            'comment': comment,
            'rating': rating
        }
    }

    reviews.append(new_review)
    with open(reviews_path,'w', encoding='utf-8') as file:
        json.dump(reviews, file, indent=4, ensure_ascii=False)

    print(f"Added for {product_name}, Commint and Rating successfully.")
    return True


# ======= SHOW REVIWES FOR PRODUCT FUNCTION =======
def show_product_reviews() -> None :

    product_name = str(input("Enter product name to show reviews : "))
    found_reviews = False 

    try :
        with open(reviews_path,'r',encoding='utf-8') as file :
            reviews = json.load(file)
    except FileNotFoundError :
        print("There are no reviews to show.")
        return False
    except json.JSONDecodeError:
        print("Reviews file is empty or corrupted.")
        return False


    for review_entry in reviews : 
        
        if product_name == review_entry.get('product_name') :
            found_reviews = True
            
            review_details = review_entry.get('review', {})
            
            print("--------------------------------")
            print(f"The comment : {review_details.get('comment', 'N/A')}")
            print(f"The rating : {review_details.get('rating', 'N/A')}")
    
    
    if found_reviews:
        print("--------------------------------")
        print(f"Finished showing all reviews for {product_name}.")
        return True
    else:
        print(f"No reviews found for product: {product_name}")
        return False


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

# ======= SORT PRODUCT FUNCTION =======
def sort_by_rating_or_most_sold() -> None:
    
    print("""
    ======== Sort Products ========
    [1] ⭐ Sort by Rating (High → Low)
    [2] 🛒 Sort by Most Sold (High → Low)
    """)

    choice = input("👉 Enter your choice: ")

    if choice == "1":
        try:
            with open(reviews_path, "r", encoding="utf-8") as file:
                ratings_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠️ Ratings file not found or empty.")
            return

        if not ratings_data:
            print("No rating data available.")
            return

        product_ratings = {}
        for item in ratings_data:
            name = item["product_name"]
            rating = float(item["review"]["rating"])
            if name in product_ratings:
                product_ratings[name].append(rating)
            else:
                product_ratings[name] = [rating]

        avg_ratings = [
            {"product_name": name, "average_rating": sum(r) / len(r)}
            for name, r in product_ratings.items()
        ]

        sorted_by_rating = sorted(avg_ratings, key=lambda x: x["average_rating"], reverse=True)

        print("\n📊 Products Sorted by Rating:\n")
        for product in sorted_by_rating:
            print("----------------------------")
            print(f"🛍️ Name: {product['product_name']}")
            print(f"⭐ Average Rating: {round(product['average_rating'], 2)}")
        print("----------------------------")

    elif choice == "2":
        
        try:
            with open(products_most_solds, "r", encoding="utf-8") as file:
                most_sold = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠️ Most sold file not found or empty.")
            return

        if not most_sold:
            print("No sold products data available.")
            return

        sorted_most_sold = sorted(most_sold, key=lambda p: p.get("number_of_solds", 0), reverse=True)
        print("\n📈 Products Sorted by Most Sold:\n")

        for product in sorted_most_sold:
            print("----------------------------")
            print(f"🛍️ Name: {product['product_name']}")
            print(f"📦 Number of Sold: {product['number_of_solds']}")
        print("----------------------------")

    else:
        print("❌ Invalid choice.")
