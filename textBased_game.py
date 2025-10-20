import json
import os



SAVE_FILE = 'savegame.json'

class Player:

    ROLES_INITIAL_STATS = {
        "Paladin": {"hp": 120, "attack": 15, "defense": 30, "xp": 0},
        "Knight":  {"hp": 140, "attack": 18, "defense": 25, "xp": 0},
    }

    ENEMIES = {
        "Goblin": {"hp": 30, "attack": 5, "defense": 2, "xp_reward": 10},
        "Slime":  {'HP': 20, 'ATK': 3, 'DEF': 1, 'XP_REWARD': 7, 'COIN_REWARD': 5}
        #"Dragon Lord":   {"hp": 200, "attack": 20, "defense": 10, "xp_reward": 150},
    }

    SHOP_ITEMS = {
    'Sword':    {'Price': 80,  'ATK': 10, 'DEF': 5},
    'Claymore': {'Price': 150, 'ATK': 20, 'DEF': 0},
    'Heal Potion': {'Price': 15, 'Effect': 50, 'Type': 'Consumable'}
    }

    LAST_BOSS = {'Name': 'Dragon Lord', 'HP': 200, 'ATK': 25, 'DEF': 15, 'XP_REWARD': 100, 'COIN_REWARD': 100}

    last_boss_unlock_level = 3
    
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

    def __init__(self, name: str, role: str, coins: int, inventory: dict):

        #Name Check
        self.name = (name or "").strip()
        if not self.name:
            self.name = "Fighter"

        #Role Check
        role = (role or "").lower().strip()
        if role not in self.ROLES_INITIAL_STATS:
            raise ValueError(f"unknown role. Choose between 1- Paladin 2- Knight")
        self.role = role

        self.stats = dict(self.ROLES_INITIAL_STATS[self.role])
        
        self.coins = 20
        self.inventory = {}
        self._validate_stats()

    #Check on Stats
    def _validate_stats(self):
        s = self.stats
        if s["hp"] <= 0 or s["attack"] < 0 or s["defense"] < 0 or s["xp"] < 0:
            print("There is a problem with your stats")

    def welcoming(self):
        print("Welcome to the game!")
        name = input("What is your character's name? ").strip()
        self.name = name
        print(f"Welcome {self.name}, Hope you enjoy the game!")


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


    def pick_role(self):
        print("Please pick a role:")

        role_names = list(self.ROLES_INITIAL_STATS.keys())

        #To print the roles
        for i, role_name in enumerate(self.ROLES_INITIAL_STATS.keys()):
            print(f"{i+1}- {role_name}")

        while True:

            role = input("Enter the number of the role: ").strip()
            #will convert each to index so the user could just pick a number, and checks if index is in correct range
            try:
                role_index = int(role) - 1
                if 0 <= role_index < len(role_names):
                    new_role = role_names[role_index]

                    self.role = new_role
                    self.stats = dict(self.ROLES_INITIAL_STATS[self.role])
                    self.stats['current_hp'] = self.stats['hp']
            
                print(f"Your role is now set to {self.role}.")
                break
            except (ValueError, IndexError):
                print("Unknown command. Try again.")
