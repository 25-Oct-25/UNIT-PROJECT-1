import json
from cryptography.fernet import Fernet
from pathlib import Path

file_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/admins.json'
key_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/key_admins.key'

def load_key():
    try:
        with open(key_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None

def login() -> bool:
    # Load users
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            admins = json.load(file)
    except Exception as e:
        print(f"Error in : {e}")
        return False

    user_name = input("Enter the user name : ").strip()
    user_password = input("Enter the password : ").strip()

    key = load_key()
    if key is None:
        print("Encryption key not found. Cannot decrypt passwords.")
        print(f"Check this path: {Path(key_path).resolve()}")
        return False

    fernet = Fernet(key)

    # Loop through users
    for admin in admins:
        store_name = admin['name']
        store_password = admin['password']

        if user_name == store_name:
            try:
                decrypted_password = fernet.decrypt(store_password.encode()).decode()
            except Exception as e:
                print(f"Error decrypting password: {e}")
                return False

            if user_password == decrypted_password:
                print("Login successful")
                return True
            else:
                print("Wrong password")
                return False

    # If loop finishes, email not found
    print("Name not found")
    return False