import json, os, hashlib

DATA_FILE = "data/users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def find_user_by_username(username):
    users = load_users()
    for user in users:
        if user["username"] == username:
            return user
    return None

def find_user_by_email(email):
    users = load_users()
    for user in users:
        if user["email"] == email:
            return user
    return None

def register():
    username = input("Enter username: ")
    if find_user_by_username(username):
        print("⚠️ User already exists.")
        return

    email = input("Enter email: ")
    if find_user_by_email(email):
        print("⚠️ Email already registered.")
        return

    password = input("Enter password: ")

    user = {
        "username": username,
        "email": email,
        "password": hash_password(password)
    }

    users = load_users()
    users.append(user)
    save_users(users)
    print("✅ Account created successfully!")

def login():
    username = input("Enter username: ")
    user = find_user_by_username(username)
    if not user:
        print("❌ User not found.")
        return None

    password = input("Enter password: ")
    if hash_password(password) == user["password"]:
        print("✅ Login successful!")
        return user
    else:
        print("❌ Incorrect password.")
        return None

def forgot_password():
    email = input("Enter your registered email to reset password: ")
    user = find_user_by_email(email)
    if not user:
        print("❌ Email not found.")
        return

    # السماح مباشرة بتغيير كلمة المرور
    new_pass = input("Enter new password: ")
    user["password"] = hash_password(new_pass)

    users = load_users()
    for u in users:
        if u["email"] == email:
            u.update(user)
    save_users(users)
    print("✅ Password reset successfully.")
