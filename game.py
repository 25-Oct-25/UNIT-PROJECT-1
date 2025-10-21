import json
import os
from textBased_game import Player

last_boss_unlock_level = 3
    
SAVE_FILE = 'savegame.json'

class Game_Data:

    ENEMIES = {
        "Goblin": {"hp": 30, "atk": 5, "def": 2, "xp": 10},
        "Slime":  {'hp': 20, 'atk': 3, 'def': 1, 'xp': 7, 'coin': 5}
    }

    LAST_BOSS = {'Name': 'Dragon Lord', 'HP': 200, 'ATK': 25, 'DEF': 15, 'XP_REWARD': 100, 'COIN_REWARD': 100}

    def __init__(self):
        self.player = None


    @staticmethod
    def save_game(player):
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(player, f, indent=4)
            print("Progress saved successfully")
        except Exception as e:
            print(f"\nSaving failed... {e}")

    @staticmethod
    def load_game():
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    player = json.load(f)
                print("\nPrevious data loaded successfully")
                return player
            except Exception:
                print("\nloading data failed...")
                return None
        else:
            return None
        
    def quit_game(self):
        pass


    def create_new_player(self):
        #print("Welcome to the game!")
        name = input("Enter your character's name: ").strip() or "Hero"
        #self.name = name

        print("Pick your role:")
        role_names = list(Player.ROLES_INITIAL_STATS.keys())

        #To print roles and stats
        for i, role_name in enumerate(role_names):
            stats = Player.ROLES_INITIAL_STATS[role_name]
            print(f"{i+1}. {role_name}")
            print(f"Stats are: HP:{stats['HP']}, ATK:{stats['ATK']}, DEF:{stats['DEF']}")
            
        while True:
            choice = input

            #will convert each to index so the user could just pick a number, and checks if index is in correct range
            try:
                #to get correct index
                role_index = int(choice) - 1
                #to check the calculated index is correct
                if 0 <= role_index < len(role_names):
                    #will retrieve the role name
                    chosen_role = role_names[role_index]
                    #creates a new instance of class player
                    self.player = Player(name=name, role=chosen_role)
                    print(f"Your role is now set to {self.role}.")
                    print(f"Your stats are: HP:{stats['HP']}, ATK:{stats['ATK']}, DEF:{stats['DEF']}")
                    break
                else:
                    print("Pick a number between 1 or 2")
            
            except (ValueError, IndexError):
                print("Unknown command. Try again.")



    #the function needs improvement
    def start_menu(self):
        print("Choose from the menu:")
        print("1- Pick a role")
        print("2- Save game")
        print("3- Load game")
        print("4- Quit game")

        cmd = input("").strip()
        mapping = {
            "1": self.pick_role,
            "2": self.save_game,
            "3": self.load_game,
            "4": self.quit_game,
        }
        action = mapping.get(cmd)
        if action:
            action()
        else:
            print("Unknown command. Try again.")



    