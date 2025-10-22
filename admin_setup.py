import os
from users.user import User
from utils.helpers import save_data


USERS_FILE = "data/users.json"

def setup_admin():
    users = {}
    username = "admin"
    password = "1234" 
    admin = User(username, password, role="admin")
    users[username] = admin.to_dict()
    os.makedirs("data", exist_ok=True)
    save_data(USERS_FILE, users)
    print("✅ Admin account created successfully!")

if __name__ == "__main__":
    setup_admin()