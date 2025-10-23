import re
from email_validator import validate_email, EmailNotValidError
from rich.console import Console
import random

console = Console()

#Check if email is valid
def get_valid_email(email_input):
    
    try:
        v = validate_email(email_input)
        return v.email
    except EmailNotValidError as e:
        console.print(f"⚠️"" Invalid email: {str(e)}", style="bold red")
        return None


#Check if password is strong enough
def validate_password(password):
    """
    تحقق من قوة الباسورد:
    - على الأقل 8 حروف
    - يحتوي على حرف كبير وحرف صغير ورقم
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

#Generate a temporary reset code.
def generate_reset_code(length=6):
    """توليد كود مؤقت لنسيان الباسورد"""
    code = "".join([str(random.randint(0,9)) for _ in range(length)])
    return code
