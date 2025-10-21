ADMIN_CREDIT ={
    "admin": "PassPass12124"
}

def login():
    """
    Prompts the user for a username and password, validates them,
    and returns True for a successful login, False otherwise.
    """
    
    username =input("Enter the user name")
    password = input("Enter the password")

    if username in ADMIN_CREDIT and ADMIN_CREDIT[username] == password:
        return True
    
    return False