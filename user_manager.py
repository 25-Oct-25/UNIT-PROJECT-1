import json
import os
import hashlib
import re

USERS_FILE = os.path.join("data", "users.json")

class UserManager:
    def __init__(self):
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_users(self):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=4)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_email(self, email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None

    def signup(self):
        print("\n--- Sign Up ---")
        email = input("Enter your email: ").strip()
        if not self.validate_email(email):
            print("Invalid email format.")
            return None

        if email in self.users:
            print("Email already registered. Please log in instead.")
            return None

        password = input("Enter your password: ").strip()
        if len(password) < 6:
            print("Password too short. Use at least 6 characters.")
            return None

        hashed_pw = self.hash_password(password)
        self.users[email] = {"password": hashed_pw}
        self.save_users()
        print("Account created successfully!")
        return email

    def login(self):
        print("\n--- Login ---")
        email = input("Enter your email: ").strip()
        password = input("Enter your password: ").strip()

        if email not in self.users:
            print("Email not registered. Please sign up first.")
            return None

        hashed_pw = self.hash_password(password)
        if self.users[email]["password"] == hashed_pw:
            print("Login successful!")
            return email
        else:
            print("Incorrect password.")
            return None
