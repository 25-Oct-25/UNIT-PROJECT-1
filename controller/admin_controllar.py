import json

file_path ='C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/products.json'
discounts_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/discounts.json'

# ------- Admin Add Product -------
def add_products () -> bool :
    
    new_product = {}

    product_catagory = str(input("Enter a catagory name : ")) 
    product_name = str(input("Enter a product name : "))
    product_price = int(input("Enter a product price : $ "))

    try : 
        with open(file_path,'r',encoding='utf-8') as file :
            products = json.load(file)
    except FileNotFoundError :
        products = []

    new_product = {
        'category':product_catagory,
        'product_name':product_name,
        'product_price':product_price
    }

    products.append(new_product)
    
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(products, file, indent=4, ensure_ascii=False)
        print("Add Product Successfully")
        return True
    except Exception as e:
        print(f"Error saving user: {e}")


# ------- Admin Edit Product -------
def edit_products() -> bool:
    
    product_name = input("Enter the name of the product you want to edit: ")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            products = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("There are no products.")
        return False

    # Find the product to edit
    found = False
    for product in products:
        if product_name == product['product_name']:
            
            found = True
            print("Product found. Enter new details:")

            product['category'] = input("Enter a new category name: ")
            product['product_name'] = input("Enter a new product name: ")
            product['product_price'] = float(input("Enter a new product price: $ "))

            break 

    if not found:
        print("Product not found.")
        return False

    # Save updated products list
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(products, file, indent=4, ensure_ascii=False)
        print("Product edited successfully.")
        return True
    except Exception as e:
        print(f"Error saving product: {e}")
        return False
    

def add_discounts() -> bool:
    """
    Allows the admin to add a new discount code and rate to the database.
    """
    print("\n--- ADD NEW DISCOUNT COUPON ---")
    
    coupon_code = input("Enter new coupon code (e.g., SAVE15): ").strip().upper()
    
    if not coupon_code:
        print("❌ Coupon code cannot be empty.")
        return False

    try:
        rate_input = input("Enter discount rate (as a percentage, e.g., 15 for 15%): ").strip()
        discount_rate = float(rate_input) / 100
        
        if not (0.01 <= discount_rate <= 1.0):
            print("❌ Discount rate must be between 1% and 100%.")
            return False
            
    except ValueError:
        print("❌ Invalid rate. Please enter a valid number.")
        return False
        
    try:
        with open(discounts_path, 'r', encoding='utf-8') as file:
            discounts = json.load(file)
            if not isinstance(discounts, dict):
                discounts = {}
    except (FileNotFoundError, json.JSONDecodeError):
        discounts = {}

    if coupon_code in discounts:
        print(f"⚠️ Coupon '{coupon_code}' already exists. Updating its rate.")
    
    discounts[coupon_code] = discount_rate 
    
    try:
        with open(discounts_path, 'w', encoding='utf-8') as file:
            json.dump(discounts, file, indent=4, ensure_ascii=False)
        
        print(f"✅ Coupon '{coupon_code}' with {discount_rate * 100:.0f}% rate added/updated successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Error saving discount data: {e}")
        return False