import json
from cryptography.fernet import Fernet
from pathlib import Path

file_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/users.json'
key_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/key.key'



def load_key():
    try:
        with open(key_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None

def login() -> tuple[bool, str]:
    # Load users
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            users = json.load(file)
    except FileNotFoundError:
        print("Please sign up first")
        return False, None
    except json.JSONDecodeError:
        print("User file is empty or corrupted")
        return False, None

    user_email = input("Enter your email: ").strip()
    user_password = input("Enter your password: ").strip()

    key = load_key()
    if key is None:
        print("Encryption key not found. Cannot decrypt passwords.")
        print(f"Check this path: {Path(key_path).resolve()}")
        return False, None

    fernet = Fernet(key)

    # Loop through users
    for user in users:
        store_email = user['email']
        store_password = user['password']

        if user_email == store_email:
            try:
                decrypted_password = fernet.decrypt(store_password.encode()).decode()
            except Exception as e:
                print(f"Error decrypting password: {e}")
                return False, None

            if user_password == decrypted_password:
                print("Login successful")
                return True, user_email
            else:
                print("Wrong password")
                return False, None

    print("Email not found — Please sign up first.")
    return False, None
