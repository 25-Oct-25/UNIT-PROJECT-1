from . import storage, services

def seed():
    storage.init_db()

    services.ensure_user("AAQ_224@hotmail..com", "Abdulrahman", "student")
    services.ensure_user("admin@example.com", "Admin User", "admin")

    initial = [
        ("Intro Python", "beginner", 0.0, "Learn Python basics: variables, loops, functions."),
        ("OOP in Python", "intermediate", 99.0, "Classes, objects, inheritance, interfaces."),
        ("Data Analysis", "intermediate", 149.0, "Pandas, CSV, simple plots."),
        ("Algorithms 101", "advanced", 199.0, "Sorting, searching, Big-O intro."),
        ("Git Essentials", "beginner", 0.0, "Learn commits, branches, merges."),
    ]
    for t, l, p, s in initial:
        services.add_course(t, l, p, s)

if __name__ == "__main__":
    seed()
    print("Seed done.")
