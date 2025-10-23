
# Import the admin password from config. Support both package and script runs.
#try:
  #  from pharmacy_v1.config.environment import admin_password
# except Exception:
   # from config.environment import admin_password

import hmac
from getpass import getpass
from dotenv import load_dotenv
import os

load_dotenv()  
admin_password = os.getenv("ADMIN_PASSWORD", "admin123")


def is_admin():
    if not admin_password:
        print("Admin password not configured.")
        return False

    password = getpass("Enter password: ")  # input hidden
    if hmac.compare_digest(password, admin_password):
        return True
    print("Incorrect password")
    return False

def admin_add(name, price, qty, expiry):
    if not is_admin():
        return
    # Ensure we have a reference to the shared inventory dict. Import lazily to avoid
    # circular imports when the package is executed in different ways.
    try:
        from pharmacy_v1.pharmacy import inventory
    except Exception:
        from pharmacy import inventory

    inventory[name] = {"price": float(price), "quantity": int(qty), "expiry": expiry}
    print(f"\n{name} added to inventory.\n")

def admin_update(name, price, qty, expiry):
    if not is_admin():
        return
    try:
        from pharmacy_v1.pharmacy import inventory, find_item_container
    except Exception:
        from pharmacy import inventory, find_item_container
    # Use the same lookup logic as the application (case-insensitive, nested)
    try:
        container, key = find_item_container(name)
    except Exception:
        container, key = (None, None)

    if container and key:
        # overwrite the item in-place
        container[key] = {"price": float(price), "quantity": int(qty), "expiry": expiry}
        print(f"\n{name} updated successfully.\n")
        return

    # Fallback: try older schema where items live at top-level or under 'medicines'
    if isinstance(inventory, dict):
        meds = inventory.get('medicines') if isinstance(inventory.get('medicines'), dict) else inventory
        if name in meds:
            meds[name] = {"price": float(price), "quantity": int(qty), "expiry": expiry}
            # ensure nested map is set back
            if 'medicines' in inventory:
                inventory['medicines'] = meds
            print(f"\n{name} updated successfully.\n")
            return

    print("\nMedicine not found.\n")

def admin_remove(name):
    if not is_admin():
        return
    try:
        from pharmacy_v1.pharmacy import inventory
    except Exception:
        from pharmacy import inventory

    if name in inventory:
        del inventory[name]
        print(f"\n{name} removed from inventory.\n")
    else:
        print("\nMedicine not found.\n")
