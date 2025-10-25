import json
import os
from system.employee import Employee

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(base_dir), "data")

def check_files():
    os.makedirs(data_dir, exist_ok=True)
    admin_path = os.path.join(data_dir, "admin.json")
    employees_path = os.path.join(data_dir, "employees.json")
    users_path = os.path.join(data_dir, "users.json")

    if not os.path.exists(admin_path) or os.path.getsize(admin_path) == 0 or open(admin_path, "r", encoding="utf-8").read().strip() == "":
        print("🔐 Let's set up your admin account:")
        username = input("Enter admin username: ")
        while True:
            password = input("Enter admin password: ")
            confirm = input("Confirm password: ")
            if password != confirm:
                print("❌ Passwords do not match.")
            elif len(password) < 6:
                print("❌ Password must be at least 6 characters.")
            elif not any(c.isdigit() for c in password):
                print("❌ Password must contain at least one number.")
            elif not any(c.isupper() for c in password):
                print("❌ Password must contain at least one uppercase letter.")
            elif not any(c.islower() for c in password):
                print("❌ Password must contain at least one lowercase letter.")
            else:
                break
        security = input("Set a security code (used for password recovery): ")
        admin_data = {"username": username, "password": password, "security": security}
        with open(admin_path, "w", encoding="utf-8") as f:
            json.dump(admin_data, f, ensure_ascii=False, indent=2)
        print("✅ Admin account created successfully.\n")
    else:
        print("🧾 Admin file detected, skipping setup.\n")

    for file_path in [employees_path, users_path]:
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("[]")

def load_employees():
    try:
        with open(os.path.join(data_dir, "employees.json"), "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            return [Employee(d["id"], d["name"], d["department"], d["position"], d["salary"]) for d in json.loads(data)]
    except:
        return []

def save_employees(employees):
    data = [{"id": e.id, "name": e.name, "department": e.department, "position": e.position, "salary": e.salary} for e in employees]
    with open(os.path.join(data_dir, "employees.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    file_path = os.path.join(data_dir, "users.json")
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            users = json.loads(data)
            if isinstance(users, dict):  
                users = [users]
            elif not isinstance(users, list):  
                users = []
            return users
    except:
        return []

def save_users(new_user):
    file_path = os.path.join(data_dir, "users.json")
    users = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    users = json.loads(content)
                    if isinstance(users, dict):  
                        users = [users]
        except:
            users = []
    users.append(new_user)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)