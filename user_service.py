import json
import os
from rich.console import Console
from email_service import send_email
from security import validate_password, get_valid_email, generate_reset_code
from hashlib import sha256

console = Console()
USERS_FILE = "users.json"


# Load all users from JSON file
def load_users():
    # Check if the file exists
    if not os.path.exists(USERS_FILE):
        return [] 
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f) # Load JSON data
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        # File is corrupted, print warning and reset
        console.print("⚠️"" users.json corrupted. Resetting...", style="#c67a7a")
        return []

def save_users(users):#Save all users to JSON file
    # Write the users list to JSON file with indentation
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Hash a password using SHA256
def hash_password(password):# Encode password to bytes and hash it
    return sha256(password.encode()).hexdigest()

#Register a new user and send confirmation email
def register_user(email, password, role, name):
      # Validate email format
    email = get_valid_email(email)
    if not email:  # إذا البريد غير صحيح
        console.print("⚠️ Registration failed: invalid email.", style="#c67a7a")
        return False

    users = load_users()# Load current users
     # Check if email already exists
    if any(u['email'].lower() == email.lower() for u in users):
        console.print("⚠️ Email already registered.", style="#c67a7a")
        return False
    
    # Add new user to the list
    users.append({
        "name": name,
        "email": email,
        "password": hash_password(password),
        "role": role
    })
    save_users(users)# Save updated users list
    console.print(f"✅ Registered successfully! Welcome [bold]{name}[/bold].", style="#8cc98e")
     # Send confirmation email
    send_email(email, "Registration Confirmation", f"Hello {name}, your registration was successful!")
    return True

# Login a user and send login confirmation email
def login_user(email, password, role):
    users = load_users()  # Load users
     # Find user by email and role
    user = next((u for u in users if u['email'].lower() == email.lower() and u['role'].lower() == role.lower()), None)
    if not user:
        console.print("⚠️"" Email not found or wrong role.", style="#c67a7a")
        return False
    
     # Check password
    if user['password'] != hash_password(password):
        console.print("⚠️"" Incorrect password.", style="#c67a7a")
        return False
    
    console.print(f"✅ Welcome back, [bold]{user['name']}[/bold]!", style="green")
    send_email(email, "Login Confirmation", f"Hello {user['name']}, you have successfully logged in!")
    return True

# Reset user password via email code
def reset_password_flow(email):
    users = load_users() # Load users
     # Find user by email
    user = next((u for u in users if u['email'].lower() == email.lower()), None)
    if not user:
        console.print("⚠️"" Email not found.", style="#c67a7a")
        return False
    
    code = generate_reset_code()
    send_email(email, "Password Reset Code", f"Your reset code is: {code}")
    console.print(f"✅ Reset code sent to {email}. Check your email!", style="#8EA891")  # احذف طباعة الكود
    entered_code = input("Enter the reset code: ")

    if entered_code.strip() != code:# Verify the code
        console.print("⚠️"" Invalid code.", style="#c67a7a")
        return False

    # Validate password strength 
    while True:
        new_password = input("Enter new password: ")
        if not validate_password(new_password):
            console.print("⚠️"" Password must be 8+ chars, include uppercase, lowercase, and number.", style="#c67a7a")
            continue

        verify_password = input("Verify new password: ")
        if new_password != verify_password:
            console.print("⚠️"" Passwords do not match.", style="#c67a7a")
            continue

 # Update password and save
        user['password'] = hash_password(new_password)
        save_users(users)
        console.print("✅ Password updated successfully!", style="#8EA891")
        return True
