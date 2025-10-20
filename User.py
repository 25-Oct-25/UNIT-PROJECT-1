import json
import os
import hashlib
import hmac
from dotenv import load_dotenv

load_dotenv()

class User:
    USERS_FILE = "data/users.json"

    def __init__(self, username, password_hash):
        self.username = username
        self._password_hash = password_hash
        self.stories = []

    @staticmethod
    def _hash_password(password):
        """
        hash password with secret key from .env
        """
        secret_key = os.getenv("ENCRYPTION_KEY", "default_key")
        return hmac.new(secret_key.encode(), password.encode(), hashlib.sha256).hexdigest()

    @property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, new_password):
        self._password_hash = self._hash_password(new_password)

    @staticmethod
    def _load_users():
        if os.path.exists(User.USERS_FILE):
            with open(User.USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def _save_users(data):
        os.makedirs(os.path.dirname(User.USERS_FILE), exist_ok=True)
        with open(User.USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def signup(cls):
        users = cls._load_users()
        username = input("Enter new username: ").strip()
        if username in users:
            print("⚠️ Username already exists!")
            return None

        password = input("Enter password: ").strip()
        hashed = cls._hash_password(password)
        users[username] = {"password": hashed}
        cls._save_users(users)
        print("Signup successful! You can log in now.")
        return cls(username, hashed)

    @classmethod
    def login(cls):
        users = cls._load_users()
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        hashed = cls._hash_password(password)

        if username in users and users[username]["password"] == hashed:
            print(f"Welcome back, {username}!")
            return cls(username, hashed)
        else:
            print("Invalid username or password.")
            return None
