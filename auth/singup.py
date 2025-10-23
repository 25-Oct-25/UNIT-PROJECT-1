import json
import random
import smtplib
from email.message import EmailMessage
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

file_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/users.json'
key_path = 'C:/Users/PC/Desktop/شهادات/Tuwaiq Academy/Python Labs/Unit-1/UNIT-PROJECT-1/database/key.key'

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# -------- Generate / Load Encryption Key --------
def load_or_create_key() -> str :
    try:
        with open(key_path, "rb") as file:
            return file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(key_path, "wb") as file:
            file.write(key)
        return key


# -------- OTP Generator --------
def otp_generator() -> str :
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


# -------- Sign Up Function --------
def sign_up() -> bool :
    # Load existing users
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = []

    user_email = input("Enter your email: ")
    user_password = input("Enter your password: ")
    confirmed_password = input("Enter your password again: ")

    if user_password != confirmed_password:
        print("Passwords do not match")
        return False

    # Encrypt the password
    key = load_or_create_key()
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(user_password.encode()).decode()

    # Generate OTP
    otp = otp_generator()

    # Send OTP email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # App password 

        msg = EmailMessage()
        msg["Subject"] = "OTP Verification Email"
        msg["From"] = "E-Store"
        msg["To"] = user_email
        msg.set_content(f"Your OTP code is: {otp}")

        server.send_message(msg)
        server.quit()
        print(f"Verification email sent to {user_email}")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")


    # Verify OTP
    input_otp = input("Enter the OTP you received: ")
    if input_otp != otp:
        print("Invalid OTP")
        return False

    # Create new user
    new_user = {
        "id": len(users) + 1,
        "email": user_email,
        "password": encrypted_password
    }

    users.append(new_user)

    # Save to file
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(users, file, indent=4, ensure_ascii=False)
        print("Sign Up Successfully")
        return True
    except Exception as e:
        print(f"Error saving user: {e}")