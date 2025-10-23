# modules/auth.py
import json
import os
import hashlib
import re
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "..", "data", "users.json")
RESET_FILE = os.path.join(BASE_DIR, "..", "data", "reset_links.json")

load_dotenv()  # Load .env vars

# ------------------ Utilities ------------------
def _ensure_file(path: str, default_content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_content, f)

def hash_password(password: str) -> str:
    """Return SHA-256 hash of the given password."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load all users from users.json (returns list)."""
    _ensure_file(DATA_FILE, [])
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else []

def save_users(users):
    """Persist users list to users.json."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def is_valid_email(email: str) -> bool:
    """Very simple email format validation (.com / .net)."""
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(com|net)$"
    return bool(re.match(pattern, email))

# ------------------ Email (Reset Link) ------------------
def _send_reset_link(email: str, token: str) -> None:
    """Send password-reset link via Gmail SMTP using app password."""
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    base_url = os.getenv("RESET_BASE_URL", "http://127.0.0.1:5000/reset")

    reset_link = f"{base_url}?email={email}&token={token}"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = email
    msg["Subject"] = "Password Reset Request"

    body = f"""Hello,

You requested to reset your password.
Click the link below to set a new password:

{reset_link}

If you didn't request this, you can ignore this email.
"""
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print(f"✅ Reset link sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send reset email: {e}")

# ------------------ Public Flows ------------------
def register():
    """Register a new user (first user becomes admin)."""
    users = load_users()

    # Username
    while True:
        username = input("Enter a username: ").strip()
        if len(username) < 3:
            print("⚠ Username must be at least 3 characters.")
            continue
        if any(u["username"].lower() == username.lower() for u in users):
            print("⚠ This username is already taken.")
            continue
        break

    # Email
    while True:
        email = input("Enter your email (e.g., name@gmail.com): ").strip()
        if not is_valid_email(email):
            print("⚠ Invalid email. Only .com or .net are accepted.")
            continue
        if any(u["email"].lower() == email.lower() for u in users):
            print("⚠ This email is already registered.")
            continue
        break

    # Password
    while True:
        password = input("Create a password (min 6 chars, no spaces): ").strip()
        if len(password) < 6 or " " in password:
            print("❌ Invalid password. Please try again.")
            continue
        confirm = input("Confirm password: ").strip()
        if confirm != password:
            print("⚠ Passwords do not match.")
            continue
        break

    role = "admin" if not users else "user"
    users.append({
        "username": username,
        "email": email,
        "password": hash_password(password),
        "role": role
    })
    save_users(users)
    print(f"✅ Registered successfully! Your role: {role.upper()}")

def login():
    """Log in with username or email. Type 'forgot' to reset password."""
    users = load_users()
    print("Login (type your username or email). Type 'forgot' if you forgot your password.")
    identifier = input("Identifier: ").strip()

    if identifier.lower() == "forgot":
        send_password_reset()
        return None

    user = next((u for u in users if u["username"].lower() == identifier.lower()
                 or u["email"].lower() == identifier.lower()), None)
    if not user:
        print("❌ No user found with this identifier.")
        return None

    pw = input("Enter your password: ").strip()
    if hash_password(pw) == user["password"]:
        print(f"✅ Login successful! Role: {user['role']}")
        return user
    else:
        print("❌ Incorrect password.")
        return None

def send_password_reset():
    """Create a reset token, store it, and email the link to the user."""
    email = input("Enter your registered email: ").strip()
    users = load_users()

    user = next((u for u in users if u["email"].lower() == email.lower()), None)
    if not user:
        print("❌ This email is not registered.")
        return

    _ensure_file(RESET_FILE, {})
    with open(RESET_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        tokens = json.loads(content) if content else {}

    # Invalidate old tokens for this email
    for t in [t for t, e in tokens.items() if e.lower() == email.lower()]:
        del tokens[t]

    token = str(uuid.uuid4())
    tokens[token] = email

    with open(RESET_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=4)

    _send_reset_link(email, token)
    print("📧 A reset link has been sent. Please check your inbox.")

def reset_password_from_link():
    """Manual flow to reset password by token (CLI fallback)."""
    token = input("Enter your reset token: ").strip()
    if not os.path.exists(RESET_FILE):
        print("❌ No reset requests found.")
        return

    with open(RESET_FILE, "r", encoding="utf-8") as f:
        tokens = json.load(f)

    email = tokens.get(token)
    if not email:
        print("❌ Invalid or expired token.")
        return

    users = load_users()
    for u in users:
        if u["email"].lower() == email.lower():
            new_pw = input("Enter a new password (min 6 chars): ").strip()
            if len(new_pw) < 6:
                print("❌ Too short.")
                return
            u["password"] = hash_password(new_pw)
            save_users(users)
            # delete the token
            del tokens[token]
            with open(RESET_FILE, "w", encoding="utf-8") as f:
                json.dump(tokens, f, indent=4)
            print("✅ Password updated successfully.")
            return