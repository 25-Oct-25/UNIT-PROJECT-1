import os
import json
from tabulate import tabulate
from colorama import Fore, Style
from system import storage
from system.storage import data_dir
from system.employee import Employee

def clear_screen():
    print("\n" + "=" * 50 + "\n")
    os.system('cls' if os.name == 'nt' else 'clear')

def admin_login():
    while True:
        try:
            with open(os.path.join(data_dir, "admin.json"), "r", encoding="utf-8") as f:
                admin = json.load(f)
        except:
            print(Fore.RED + "Admin file not found." + Style.RESET_ALL)
            return False
        print("\n1. Login")
        print("2. Forgot Password")
        print("3. Back\n")
        choice = input("Choose: ")

        if choice == "1":
            while True:
                user = input("Admin username: ")
                pw = input("Admin password: ")
                if user == admin["username"] and pw == admin["password"]:
                    print(Fore.GREEN + f"\n👑 Logged in as Admin ({user})\n" + Style.RESET_ALL)
                    return True
                else:
                    print(Fore.RED + "❌ Wrong username or password.\n" + Style.RESET_ALL)
                    again = input("Try again? (y/n): ").lower()
                    if again != "y":
                        break

        elif choice == "2":
            user = input("Enter admin username: ")
            if user != admin["username"]:
                print(Fore.RED + "❌ Username not found.\n" + Style.RESET_ALL)
                continue
            code = input("Enter your security code: ")
            if code == admin.get("security"):
                new_pw = input("Enter new password: ")
                confirm = input("Confirm new password: ")
                if new_pw == confirm and len(new_pw) >= 6:
                    admin["password"] = new_pw
                    with open(os.path.join(data_dir, "admin.json"), "w", encoding="utf-8") as f:
                        json.dump(admin, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + "✅ Password reset successfully.\n" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ Passwords do not match or too short.\n" + Style.RESET_ALL)
            else:
                print(Fore.RED + "❌ Incorrect security code.\n" + Style.RESET_ALL)

        elif choice == "3":
            return False
        else:
            print(Fore.RED + "❌ Invalid choice. Please try again.\n" + Style.RESET_ALL)

def user_login():
    while True:
        users = storage.load_users()
        username = input("Username: ")
        pw = input("Password: ")
        for u in users:
            if u["username"] == username and u["password"] == pw:
                print(Fore.GREEN + f"\n✅ Welcome {username}! You are now logged in.\n" + Style.RESET_ALL)
                return username
        print(Fore.RED + "❌ Invalid login.\n" + Style.RESET_ALL)
        again = input("Try again? (y/n): ").lower()
        if again != "y":
            return None

def add_user():
    while True:
        name = input("New username: ")
        pw = input("New password: ")
        if not name or not pw:
            print("❌ Username and password cannot be empty.\n")
            continue
        users = storage.load_users()
        if any(u["username"] == name for u in users):
            print("❌ User already exists.\n")
            continue
        storage.save_users({"username": name, "password": pw})
        users = storage.load_users()
        print(Fore.GREEN + f"✅ User '{name}' created. (Total users: {len(users)})\n" + Style.RESET_ALL)
        input(Fore.MAGENTA + "Press Enter to continue..." + Style.RESET_ALL)
        break

def list_users():
    users = storage.load_users()
    if not users:
        print(Fore.YELLOW + "No users yet.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")
        return
    print(Fore.CYAN + "\n📋 Registered Users:\n" + Style.RESET_ALL)
    table = []
    for u in users:
        name = u.get("username", "Unknown")
        pw = u.get("password", "*")
        table.append([name, "******"])
    print(Fore.YELLOW + tabulate(table, headers=["Username", "Password"], tablefmt="grid") + Style.RESET_ALL)
    print()
    input(Fore.MAGENTA + "Press Enter to return..." + Style.RESET_ALL)

def update_user():
    users = storage.load_users()
    if not users:
        print(Fore.YELLOW + "No users to update.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")
        return

    print(Fore.CYAN + "\n📋 Current Users:\n" + Style.RESET_ALL)
    for i, u in enumerate(users, 1):
        print(f"{i}. {u['username']}")

    try:
        index = int(input("\nChoose user number to update: ")) - 1
        if index < 0 or index >= len(users):
            print(Fore.RED + "❌ Invalid choice.\n" + Style.RESET_ALL)
            input("Press Enter to continue...")
            return
    except:
        print(Fore.RED + "❌ Invalid number.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")
        return

    user = users[index]
    print(Fore.CYAN + f"\nEditing user: {user['username']}\n" + Style.RESET_ALL)
    print(Fore.YELLOW + tabulate([
        ["1", "Username", user["username"]],
        ["2", "Password", "******"]
 ], headers=["No", "Field", "Current Value"], tablefmt="grid") + Style.RESET_ALL)

    choice = input("Choose field number to update (1-2): ").strip()
    if choice == "1":
        new_username = input("New username: ").strip()
        if not new_username:
            print(Fore.RED + "❌ Value cannot be empty.\n" + Style.RESET_ALL)
            input("Press Enter to continue...")
            return
        if any(u["username"] == new_username for u in users if u is not user):
            print(Fore.RED + "❌ Username already exists.\n" + Style.RESET_ALL)
            input("Press Enter to continue...")
            return
        user["username"] = new_username
    elif choice == "2":
        new_password = input("New password: ").strip()
        if not new_password:
            print(Fore.RED + "❌ Value cannot be empty.\n" + Style.RESET_ALL)
            input("Press Enter to continue...")
            return
        user["password"] = new_password
    else:
        print(Fore.RED + "❌ Invalid choice.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")
        return

    with open(os.path.join(data_dir, "users.json"), "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    print(Fore.GREEN + "✅ User updated successfully.\n" + Style.RESET_ALL)
    input("Press Enter to continue...")

def delete_user():
    users = storage.load_users()
    if not users:
        print(Fore.YELLOW + "No users to delete.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")
        return

    print(Fore.CYAN + "\n📋 Current Users:\n" + Style.RESET_ALL)
    for i, u in enumerate(users, 1):
        print(f"{i}. {u['username']}")

    try:
        index = int(input("\nChoose user number to delete: ")) - 1
        if index < 0 or index >= len(users):
            print(Fore.RED + "❌ Invalid choice.\n" + Style.RESET_ALL)
            input("Press Enter to continue...")
            return
    except:
        print(Fore.RED + "❌ Invalid number.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")
        return

    confirm = input(f"Are you sure you want to delete '{users[index]['username']}'? (y/n): ").lower()
    if confirm == "y":
        del users[index]
        with open(os.path.join(data_dir, "users.json"), "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        print(Fore.GREEN + "✅ User deleted successfully.\n" + Style.RESET_ALL)
    else:
        print(Fore.CYAN + "❎ Deletion canceled.\n" + Style.RESET_ALL)

    input("Press Enter to continue...")

def add_employee(employees):
    while True:
        name = input("Name: ").strip()
        if not name:
            print(Fore.RED + "❌ Name cannot be empty.\n" + Style.RESET_ALL)
            continue
        dept = input("Department: ").strip()
        if not dept:
            print(Fore.RED + "❌ Department cannot be empty.\n" + Style.RESET_ALL)
            continue
        pos = input("Position: ").strip()
        if not pos:
            print(Fore.RED + "❌ Position cannot be empty.\n" + Style.RESET_ALL)
            continue
        while True:
            sal = input("Salary: ").strip()
            if not sal:
                print(Fore.RED + "❌ Salary cannot be empty.\n" + Style.RESET_ALL)
                continue
            try:
                sal = float(sal)
                break
            except:
                print(Fore.RED + "❌ Salary must be a number.\n" + Style.RESET_ALL)
        emp_id = employees[-1].id + 1 if employees else 1
        emp = Employee(emp_id, name, dept, pos, sal)
        employees.append(emp)
        storage.save_employees(employees)
        print(Fore.GREEN + f"✅ Employee '{name}' added successfully.\n" + Style.RESET_ALL)
        input(Fore.MAGENTA + "Press Enter to continue..." + Style.RESET_ALL)
        break

def list_employees(employees):
    if not employees:
        print("No employees.\n")
        input("Press Enter to continue...")
        return
    table = []
    for e in employees:
        table.append([
            f"💼 {e.id}",
            e.name,
            e.department,
            e.position,
            f"{e.salary:.2f} ✅"
        ])
    print(Fore.YELLOW + tabulate(table, headers=["ID", "Name", "Department", "Position", "Salary"], tablefmt="grid") + Style.RESET_ALL)
    print()
    input(Fore.MAGENTA + "Press Enter to return..." + Style.RESET_ALL)

def search_employee(employees):
    key = input("Search keyword: ").lower().strip()
    if not key:
        print(Fore.RED + "❌ You must enter something to search.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")
        return
    found = []
    for e in employees:
        if key in e.name.lower() or key in e.department.lower() or key in e.position.lower():
            found.append([f"💼 {e.id}", e.name, e.department, e.position, f"{e.salary:.2f} ✅"])
    if found:
        print(Fore.YELLOW + tabulate(found, headers=["ID", "Name", "Department", "Position", "Salary"], tablefmt="grid") + Style.RESET_ALL)
    else:
        print(Fore.RED + "No results found.\n" + Style.RESET_ALL)
    input(Fore.MAGENTA + "Press Enter to continue..." + Style.RESET_ALL)

def update_employee(employees):
    if not employees:
        print(Fore.YELLOW + "No employees to update.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")
        return

    while True:
        try:
            emp_id = int(input("Employee ID: "))
            break
        except:
            print(Fore.RED + "❌ Please enter a valid number.\n" + Style.RESET_ALL)

    found = False
    for e in employees:
        if e.id == emp_id:
            found = True
            print(Fore.CYAN + f"\nEditing employee: {e.name}\n" + Style.RESET_ALL)
            print(Fore.YELLOW + tabulate([
                ["1", "Name", e.name],
                ["2", "Department", e.department],
                ["3", "Position", e.position],
                ["4", "Salary", e.salary]
            ], headers=["No", "Field", "Current Value"], tablefmt="grid") + Style.RESET_ALL)

            choice = input("Choose field number to update (1-4): ").strip()
            fields = {"1": "name", "2": "department", "3": "position", "4": "salary"}

            if choice not in fields:
                print(Fore.RED + "❌ Invalid choice.\n" + Style.RESET_ALL)
                input("Press Enter to continue...")
                return

            new_value = input(f"Enter new {fields[choice].capitalize()}: ").strip()
            if not new_value:
                print(Fore.RED + "❌ Value cannot be empty.\n" + Style.RESET_ALL)
                input("Press Enter to continue...")
                return

            if fields[choice] == "salary":
                try:
                    new_value = float(new_value)
                except:
                    print(Fore.RED + "❌ Salary must be a number.\n" + Style.RESET_ALL)
                    input("Press Enter to continue...")
                    return

            setattr(e, fields[choice], new_value)
            storage.save_employees(employees)
            print(Fore.GREEN + f"✅ Employee '{e.name}' updated successfully.\n" + Style.RESET_ALL)
            input("Press Enter to continue...")
            return

    if not found:
        print(Fore.RED + "❌ Employee not found.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")

def delete_employee(employees):
    if not employees:
        print(Fore.YELLOW + "No employees to delete.\n" + Style.RESET_ALL)
        input("Press Enter to continue...")
        return
    while True:
        try:
            emp_id = int(input("Employee ID to delete: "))
            break
        except:
            print(Fore.RED + "❌ Please enter a valid number.\n" + Style.RESET_ALL)
    for e in employees:
        if e.id == emp_id:
            confirm = input(f"Are you sure you want to delete {e.name}? (y/n): ").lower()
            if confirm == "y":
                employees.remove(e)
                storage.save_employees(employees)
                print(Fore.GREEN + f"✅ Employee '{e.name}' deleted.\n" + Style.RESET_ALL)
            else:
                print(Fore.CYAN + "❎ Deletion canceled.\n" + Style.RESET_ALL)
            input("Press Enter to continue...")
            return
    print(Fore.RED + "❌ Employee not found.\n" + Style.RESET_ALL)
    input("Press Enter to continue...")

def sort_by_department(employees):
    if not employees:
        print("No employees.\n")
        input("Press Enter to continue...")
        return
    sorted_emps = sorted(employees, key=lambda e: e.department.lower())
    table = [[f"💼 {e.id}", e.name, e.department, e.position, f"{e.salary:.2f} ✅"] for e in sorted_emps]
    print(Fore.YELLOW + tabulate(table, headers=["ID", "Name", "Department", "Position", "Salary"], tablefmt="grid") + Style.RESET_ALL)
    print()
    input(Fore.MAGENTA + "Press Enter to return..." + Style.RESET_ALL)

def sort_by_salary(employees):
    if not employees:
        print("No employees.\n")
        input("Press Enter to continue...")
        return
    sorted_emps = sorted(employees, key=lambda e: e.salary, reverse=True)
    table = [[f"💼 {e.id}", e.name, e.department, e.position, f"{e.salary:.2f} ✅"] for e in sorted_emps]
    print(Fore.YELLOW + tabulate(table, headers=["ID", "Name", "Department", "Position", "Salary"], tablefmt="grid") + Style.RESET_ALL)
    print()
    input(Fore.MAGENTA + "Press Enter to return..." + Style.RESET_ALL)

def admin_menu():
    clear_screen()
    data = [
        ["1", "Create user"],
        ["2", "List users"],
        ["3", "Update user"],
        ["4", "Delete user"],
        ["5", "Manage employees"],
        ["6", "Logout"]
    ]
    print(Fore.CYAN + tabulate(data, headers=["Option", "Admin Tasks"], tablefmt="grid") + Style.RESET_ALL)

def user_menu(username):
    clear_screen()
    data = [
        ["1", "Add employee"],
        ["2", "List employees"],
        ["3", "Update employee"],
        ["4", "Delete employee"],
        ["5", "Logout"],
        ["6", "More options"]
    ]
    print(Fore.CYAN + f"\n👋 Hello {username}, welcome!\n" + Style.RESET_ALL)
    print(Fore.YELLOW + tabulate(data, headers=["Option", "Description"], tablefmt="grid") + Style.RESET_ALL)

def admin_panel():
    while True:
        admin_menu()
        choice = input("Choose: ")
        if choice == "1":
            add_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            update_user()
        elif choice == "4":
            delete_user()
        elif choice == "5":
            employee_panel("Admin")
        elif choice == "6":
            print(Fore.CYAN + "Logged out.\n" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "❌ Invalid choice. Try again.\n" + Style.RESET_ALL)

def employee_panel(username):
    employees = storage.load_employees()
    while True:
        user_menu(username)
        choice = input("Choose: ")
        if choice == "1":
            add_employee(employees)
        elif choice == "2":
            list_employees(employees)
        elif choice == "3":
            update_employee(employees)
        elif choice == "4":
            delete_employee(employees)
        elif choice == "5":
            print(Fore.CYAN + "Logged out.\n" + Style.RESET_ALL)
            break
        elif choice == "6":
            extra_features(employees)
        else:
            print(Fore.RED + "❌ Invalid choice. Try again.\n" + Style.RESET_ALL)

def extra_features(employees):
    while True:
        clear_screen()
        data = [
            ["1", "Search employee"],
            ["2", "Sort by department"],
            ["3", "Sort by salary"],
            ["4", "Back to main menu"]
        ]
        print(Fore.MAGENTA + tabulate(data, headers=["Option", "Feature"], tablefmt="grid") + Style.RESET_ALL)
        choice = input("Choose: ")
        if choice == "1":
            search_employee(employees)
        elif choice == "2":
            sort_by_department(employees)
        elif choice == "3":
            sort_by_salary(employees)
        elif choice == "4":
            print(Fore.CYAN + "Returning to main menu...\n" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "❌ Invalid choice. Try again.\n" + Style.RESET_ALL)

def start():
    print(Fore.CYAN + "\n🔍 Checking system files... please wait.\n" + Style.RESET_ALL)
    storage.check_files()
    while True:
        clear_screen()
        data = [
            ["1", "Login as Admin"],
            ["2", "Login as User"],
            ["3", "Exit"]
        ]
        print(Fore.BLUE + tabulate(data, headers=["Option", "Main Menu"], tablefmt="grid") + Style.RESET_ALL)
        choice = input("Choose: ")
        if choice == "1":
            if admin_login():
                admin_panel()
        elif choice == "2":
            username = user_login()
            if username:
                employee_panel(username)
        elif choice == "3":
            print(Fore.CYAN + "Goodbye 👋" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "❌ Invalid option. Try again.\n" + Style.RESET_ALL)