import os
from dotenv import load_dotenv

load_dotenv()

print("EMAIL_USER =", os.getenv("EMAIL_USER"))
print("EMAIL_PASS =", os.getenv("EMAIL_PASS"))
print("RESET_BASE_URL =", os.getenv("RESET_BASE_URL"))