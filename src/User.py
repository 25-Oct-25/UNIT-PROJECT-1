#Built-in modules
import json
import os
import hashlib
import hmac
from getpass import getpass
#External libraries
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)
load_dotenv()


class User:


    USERS_FILE = "data/users.json"

    def __init__(self, username, password_hash):
        """Initialize a new user instance."""
        self.username = username
        self._password_hash = password_hash

    # PASSWORD HANDLING 

    @staticmethod
    def _hash_password(password):
        """Hash password using HMAC with a secret key from .env."""
        secret_key = os.getenv("ENCRYPTION_KEY")
        if not secret_key:
            raise ValueError("Missing ENCRYPTION_KEY in .env file.")
        return hmac.new(secret_key.encode(), password.encode(), hashlib.sha256).hexdigest()

    @property
    def password_hash(self):
        """Return hashed password."""
        return self._password_hash

    @password_hash.setter
    def password_hash(self, new_password):
        """Update stored password securely."""
        self._password_hash = self._hash_password(new_password)

    # USER DATA FILE HANDLING 

    @staticmethod
    def _load_users():
        """Load all users from JSON file."""
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

    @staticmethod
    def _is_strong_password(password):
        """
        Check if password meets complexity requirements:
        - At least 8 characters
        - Contains uppercase, lowercase, number, and symbol
        """
        import re
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[@$!%*?&#]", password):
            return False
        return True
    
    @classmethod
    def reset_password(cls):
        """Allow user to reset password if they forgot it."""
        users = cls._load_users()
        print(Fore.CYAN + "\n🔄 Reset your password" + Fore.RESET)
        username = input("Enter your username: ").strip().lower()

        if username not in users:
            print(Fore.RED + "❌ Username not found.")
            return None

        new_password = input("Enter a new password: ").strip()
        confirm = input("Confirm new password: ").strip()

        if new_password != confirm:
            print(Fore.RED + "❌ Passwords do not match.")
            return None

        if not cls._is_strong_password(new_password):
            print(Fore.YELLOW + "⚠️ Weak password! Try a stronger one.")
            return None

        users[username]["password"] = cls._hash_password(new_password)
        cls._save_users(users)

        print(Fore.GREEN + f"✅ Password reset successful for {username.capitalize()}!")
        print(Fore.CYAN + "--------------------------------------" + Fore.RESET)
        return cls(username, users[username]["password"])



    # AUTHENTICATION LOGIC 

    @classmethod
    def signup(cls):
        """Register a new user securely."""
        users = cls._load_users()
        print(Fore.CYAN + "\n📝 Create a new account" + Fore.RESET)
        username = input("Enter a new username: ").strip().lower()

        if username in users:
            print(Fore.YELLOW + "⚠️ Username already exists! Please choose another one.")
            return None
        
        password = getpass("Enter a password: ").strip()

        if not cls._is_strong_password(password):
            print(Fore.YELLOW + "⚠️ Weak password! Use at least 8 characters with uppercase, lowercase, numbers, and symbols.")
            return None
        
        confirm = getpass("Confirm password: ").strip()

        if confirm != password:
            print(Fore.RED + "❌ Passwords do not match. Try again.")
            print(Fore.CYAN + "--------------------------------------" + Fore.RESET)
            return None

        hashed = cls._hash_password(password)
        users[username] = {"password": hashed}
        cls._save_users(users)

        print(Fore.GREEN + f"✅ Signup successful! Welcome, {username.capitalize()}!")
        print(Fore.CYAN + "--------------------------------------" + Fore.RESET)
        return cls(username, hashed)

    @classmethod
    def login(cls):
        """Authenticate existing user."""
        users = cls._load_users()
        print(Fore.CYAN + "\n🔐 Login to your account" + Fore.RESET)
        username = input("Username: ").strip().lower()
        password = getpass("Password: ").strip()
        hashed = cls._hash_password(password)

        if username in users and users[username]["password"] == hashed:
            print(Fore.LIGHTGREEN_EX + f"✅ Welcome back, {username.capitalize()}!")
        else:
            print(Fore.RED + "❌ Invalid username or password. Please try again.")
            forgot = input(Fore.YELLOW + "Forgot your password? (y/n): ").strip().lower()
            if forgot == "y":
                cls.reset_password()
                return None

            print(Fore.CYAN + "--------------------------------------" + Fore.RESET)
            return None

        print(Fore.CYAN + "--------------------------------------" + Fore.RESET)
        return cls(username, hashed)
