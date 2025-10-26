 ## Employee Management 

 ## Overview

This project is a Command Line Interface (CLI) based Employee Management System.
It allows an Admin to manage employees and users directly through the terminal.
The system is designed to be simple, organized, and easy to use.
All data is stored safely using JSON files.

There are two types of users:
	•	Admin → manages users and employees.
	•	User → manages employees only.

⸻

 ## Features & User Stories

As an Admin I can:
	•	Create new users.
	•	List existing users.
	•	Update a user’s information.
	•	Delete users from the system.
	•	Manage employees (add, update, delete, sort, search).
	•	View all employees in organized tables.
	•	Logout securely.

As a User I can:
	•	Add new employees to the system.
	•	List employees in a table format.
	•	Update employee information (name, department, position, salary).
	•	Delete employees from the system.
	•	Search for employees by name, department, or position.
	•	Sort employees by department or salary.
	•	Logout safely.

⸻

 ## System Structure

employee_managemant/
│
├── main.py                # Program entry point
├── data/                  # Stores JSON data
│   ├── admin.json
│   ├── employees.json
│   └── users.json
│
└── system/                # Core modules
    ├── employee.py        # Employee class
    ├── storage.py         # Handles file operations
    └── logic.py           # Contains program logic and menus


⸻

 ## Usage

1. Run the program

python main.py

2. Main Menu
	•	1 → Login as Admin
	•	2 → Login as User
	•	3 → Exit

3. Admin Menu
	•	1 → Create user
	•	2 → List users
	•	3 → Update user
	•	4 → Delete user
	•	5 → Manage employees
	•	6 → Logout

4. User Menu
	•	1 → Add employee
	•	2 → List employees
	•	3 → Update employee
	•	4 → Delete employee
	•	5 → Logout
	•	6 → More options (Search, Sort by department, Sort by salary)

5. Examples
	•	Add employee → enter name, department, position, salary.
	•	Update employee → choose by ID and select which field to edit.
	•	Delete employee → confirm before deletion.
	•	Search employee → enter a keyword (like “IT” or “Manager”).
	•	Sort employees → by department or salary.

⸻

 ## Technologies Used
	•	Python 3
	•	Colorama (for colored terminal output)
	•	Tabulate (for table display)
	•	JSON (for data storage)

⸻

 ## Summary

This Employee Management System demonstrates how to:
	•	Organize code using modules and packages in Python.
	•	Manage users and employees interactively through the terminal.
	•	Handle data storage and display information in a structured way.