import json
import sys
import time
import os
import platform
from utils.colors import *
from utils.art_assets import TIME_ARCADE_LOGO

# -------------------------------
#         JSON Helpers
# -------------------------------

def load_data(filepath: str) -> dict:
    """
    Load JSON data from a file.
    Returns an empty dict if the file does not exist or is invalid.
    """
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(RED + f"⚠️ Error reading {filepath}. Returning empty data." + RESET)
        return {}


def save_data(filepath: str, data: dict):
    """
    Save data to a JSON file with indentation for readability.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# -------------------------------
#          CLI Helpers
# -------------------------------

def clear_screen():
    """
    Clear the terminal screen.
    """
    os.system("cls" if platform.system() == "Windows" else "clear")


def animated_welcome():
    """
    Show animated welcome message with ASCII art and optional voice.
    Works on Windows, Linux, Mac.
    """
    print(CYAN + TIME_ARCADE_LOGO + RESET)
    time.sleep(0.8)

    print(BLUE+""+RESET)
    line = "⚡ Where History Becomes Your Playground ⚡"
    for char in line:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.05)
    print("\n")
    time.sleep(0.5)

    try:
        if platform.system() == "Darwin":
            os.system("say 'Welcome to Time Arcade'")
    except Exception:
        pass

    print("Loading", end="", flush=True)
    for _ in range(3):
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(0.5)
    print("\n")