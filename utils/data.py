import json
import sys, time, os
import platform
from utils.colors import *
from utils.art_assets import TIME_ARCADE_LOGO

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
        
def animated_welcome():
    print(CYAN + TIME_ARCADE_LOGO + RESET)
    time.sleep(0.8)

    line = YELLOW + "⚡ Where History Becomes Your Playground ⚡" + RESET
    for char in line:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.05)
    print("\n")
    time.sleep(0.5)

    
    try:
        if os.name == "posix":
            os.system("say 'Welcome to Time Arcade'")
    except:
        pass

    print("Loading", end="")
    for dot in "...":
        sys.stdout.write(dot)
        sys.stdout.flush()
        time.sleep(0.5)
    print("\n")

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")