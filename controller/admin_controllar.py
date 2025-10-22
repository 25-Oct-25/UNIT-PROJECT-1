import json

file_path ='C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/products.json'

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