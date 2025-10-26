class Employee:
    def __init__(self, id, name, department, position, salary):
        self.id = id
        self.name = name
        self.department = department
        self.position = position
        self.salary = salary

    def show_info(self):
        print(f"ID: {self.id}, Name: {self.name}, Department: {self.department}, Position: {self.position}, Salary: {self.salary}")