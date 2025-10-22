import json
import os
import hashlib
import hmac
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class User:
    """
    Represents a registered user who can log in and save stories.
    Handles secure password hashing using a secret key from .env.
    """

    USERS_FILE = "data/users.json"

    def __init__(self, username, password_hash):
        """
        Initialize a new user instance.

        Args:
            username (str): The user's name.
            password_hash (str): The hashed password.
        """
        self.username = username
        self._password_hash = password_hash

    # ============================================================
    # PASSWORD HANDLING
    # ============================================================

    @staticmethod
    def _hash_password(password):
        """
        Hashes a password using HMAC with a secret key from .env.

        Args:
            password (str): The plain text password.

        Returns:
            str: The hashed password string.
        """
        secret_key = os.getenv("ENCRYPTION_KEY")
        if not secret_key:
            raise ValueError("Missing ENCRYPTION_KEY in .env file.")
        return hmac.new(secret_key.encode(), password.encode(), hashlib.sha256).hexdigest()

    @property
    def password_hash(self):
        """Return the hashed password."""
        return self._password_hash

    @password_hash.setter
    def password_hash(self, new_password):
        """Update the stored password hash securely."""
        self._password_hash = self._hash_password(new_password)

    # ============================================================
    # USER DATA FILE HANDLING
    # ============================================================

    @staticmethod
    def _load_users():
        """
        Load all users from JSON file.
        Returns an empty dict if file doesn't exist or is corrupted.
        """
        if not os.path.exists(User.USERS_FILE):
            return {}
        try:
            with open(User.USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    @staticmethod
    def _save_users(data):
        """Save all users to JSON file."""
        os.makedirs(os.path.dirname(User.USERS_FILE), exist_ok=True)
        with open(User.USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ============================================================
    # AUTHENTICATION LOGIC
    # ============================================================

    @classmethod
    def signup(cls):
        """
        Register a new user.
        Ensures usernames are unique and passwords securely hashed.
        """
        users = cls._load_users()
        username = input("Enter a new username: ").strip().lower()

        if username in users:
            print("⚠️ Username already exists! Please choose another one.")
            return None

        password = input("Enter a password: ").strip()
        hashed = cls._hash_password(password)
        users[username] = {"password": hashed}
        cls._save_users(users)
        print("✅ Signup successful! You can log in now.")
        return cls(username, hashed)

    @classmethod
    def login(cls):
        """
        Log in an existing user by verifying credentials.
        Returns a User instance if successful, otherwise None.
        """
        users = cls._load_users()
        username = input("Username: ").strip().lower()
        password = input("Password: ").strip()
        hashed = cls._hash_password(password)

        if username in users and users[username]["password"] == hashed:
            print(f"✅ Welcome back, {username}!")
            return cls(username, hashed)
        else:
            print("❌ Invalid username or password. Please try again.")
            return None
