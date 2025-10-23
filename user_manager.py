# user_manager.py

from bookstore_data import users_db, save_data

def register_user(username, password, email):
    """Registers a new user."""
    if username in users_db:
        print("This username already exists. Please choose another.")
        return False
    users_db[username] = {
        "password": password,
        "email": email, # Added email
        "address": {},
        "purchase_history": [],
        "cart": {}
    }
    save_data() # Save changes
    print(f"User '{username}' registered successfully.")
    return True

def login_user(username, password):
    """Logs in a user."""
    user_data = users_db.get(username)
    if user_data and user_data["password"] == password:
        print(f"Welcome, {username}!")
        return True
    print("Invalid username or password.")
    return False

def set_shipping_address(username, street, city, state, zip_code):
    """Sets the user's shipping address."""
    if username not in users_db:
        print("Error: User does not exist.")
        return False
    users_db[username]["address"] = {
        "street": street,
        "city": city,
        "state": state,
        "zip_code": zip_code
    }
    save_data() # Save changes
    print("Your shipping address has been updated successfully.")
    return True

def get_shipping_address(username):
    """Gets the user's shipping address."""
    if username in users_db:
        address = users_db[username]["address"]
        if address:
            return address
    return None

def get_user_email(username):
    """Gets the user's email address."""
    if username in users_db:
        return users_db[username].get('email')
    return None

def is_admin(username):
    """Checks if the user is an administrator."""
    user_data = users_db.get(username)
    return user_data and user_data.get("is_admin", False)