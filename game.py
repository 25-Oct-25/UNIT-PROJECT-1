import json
import os
from textBased_game import Player
import random

LAST_BOSS_UNLOCK_LEVEL = 3
    
SAVE_FILE = 'savegame.json'

class Game:

    ENEMIES = {
        "Enemy1": {'Name': 'Goblin', 'HP': 30, 'ATK': 10, 'DEFENSE': 2, 'XP': 10, 'COIN': 40},
        "Enemy2":  {'Name': 'Slime', 'HP': 20, 'ATK': 10, 'DEFENSE': 1, 'XP': 7, 'COIN': 40}
    }

    LAST_BOSS = {'Name': 'Dragon Lord', 'HP': 200, 'ATK': 25, 'DEFENSE': 15, 'XP': 100, 'COIN': 100}

    def __init__(self):
        self.player = None
        self.running = True


    @staticmethod
    def save_game(player):
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(player.__dict__, f, indent=4)
            print("Progress saved successfully")
        except Exception as e:
            print(f"\nSaving failed... {e}")

    @staticmethod
    def load_game():
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    player = json.load(f)
                print("\nData loaded successfully")
                return player
            except Exception:
                print("\nLoading data failed...")
                return None
        else:
            return None
        
    def quit_game(self):
        self.running = False


    def create_new_player(self):
        name = input("\nEnter your character's name: ").strip() or "Hero"

        print("\nPick your role:")
        role_names = list(Player.ROLES_INITIAL_STATS.keys())

        #To print roles and stats
        for i, role_name in enumerate(role_names):
            stats = Player.ROLES_INITIAL_STATS[role_name]
            print(f"{i+1}. {role_name}")
            print(f"Stats are: HP: {stats['HP']}, ATK: {stats['ATK']}, DEF: {stats['DEFENSE']}\n")
            
        while True:
            choice = input("Your choice is: ")

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
                    print(f"\nYour role is now set to {self.player.role}.")
                    print(f"Your stats are: HP:{self.player.current_hp}/{self.player.max_hp}, ATK:{self.player.atk}, DEF:{self.player.defense}")
                    break
                else:
                    print("Pick a number 1 or 2")
            
            except (ValueError, IndexError):
                print("Unknown command. Try again.")

    def fight(self, enemy: dict):
            enemy = enemy.copy()

            base_player_def = getattr(self.player, "defense", 0)
            base_enemy_def = enemy.get("DEFENSE", enemy.get("DEF", 0))
    
            while self.player.current_hp > 0 and enemy.get('HP', 0) > 0:
                print(f"\nGet ready to fight {enemy.get('Name', enemy.get('NAME', 'Enemy'))}")

                print("\nChoose an action:")
                print("1. Attack")
                print("2. Defend")
                print("3. Use healing potion")

                player_action = input("\nYour action: ").strip()

                #to set defense each round
                self.player.defense = base_player_def
                enemy['DEFENSE'] = base_enemy_def

                if player_action == '1':
                    raw_player_damage = self.player.atk - enemy.get('DEFENSE', 0)
                    player_damage = max(0, raw_player_damage)
                    enemy['HP'] = max(0, enemy.get('HP', 0) - player_damage)
                    print(f"\nYou hit the {enemy.get('Name')} for {player_damage} damage. Enemy HP: {enemy.get('HP')}")
                
                elif player_action == '2':
                    #Increase defense for this turn
                    self.player.defense = int(base_player_def * 1.5)
                    print("\nYou brace yourself for an attack.")

                elif player_action == '3':
                    self.player.use_item('Heal Potion')

                else:
                    print("Invalid choice - you lose your turn")

                #check if enemy is defeated
                if enemy.get('HP', 0) <= 0:
                    print(f"\nCongratulation you defeated the {enemy.get('Name')}!")
                    break

                enemy_action = random.choice(["attack", "defense"])
                if enemy_action == "attack":
                    raw_enemy_damage = enemy.get('ATK', 0) - getattr(self.player, 'defense', 0)
                    enemy_damage = max(0, raw_enemy_damage)
                    self.player.current_hp = max(0, self.player.current_hp - enemy_damage)
                    print(f"\nThe {enemy.get('Name')} attacked you for {enemy_damage} damage. Your HP: {self.player.current_hp}")
                
                elif enemy_action == "defense":
                    enemy['DEFENSE'] = int(base_enemy_def * 1.5)
                    print(f"\nThe {enemy.get('Name')} braces for your attack.")


                self.player.defense = base_player_def 
                enemy['DEFENSE'] = base_enemy_def

                #Check if player is defeated
                if self.player.current_hp <= 0:
                    print(f"\nYou have been defeated...")
                    break

                
    def start_menu(self):
        print("-" * 40)
        print("*** Welcome to the text-base RPG Game! ***")
        print("-" * 40)
        
        while self.player is None:
            print("\n*** Main Menu ***")
            print("1. Start a new game")
            print("2. Load previous data")
            print("3. Exit game")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.create_new_player()
            
            elif choice == '2':
                self.load_game
                data = self.load_game()
                if data:
                    self.player = Player(loaded_data=data)
            
            elif choice == '3':
                print("Goodbye. Coma back soon!")
                return
                
            else:
                print("Invalid choice, choose from the menu")


    def main_game_loop(self):
        while self.running and self.player and self.player.current_hp > 0:
            self.player.display_stats()
            
            print("\n*** Actions Menu ***")
            print("1. Fighting a random boss")
            print("2. Open shop")
            print("3. Use Healing Potion")
  
            #Condition for the last boss
            if self.player.level >= LAST_BOSS_UNLOCK_LEVEL:
                print("4. Fight last boss")
                
            print("5. Save game")
            print("6. Exit game")
            
            choice = input("\nEnter action number: ")
            
            if choice == '1':
                enemy_name = random.choice(list(self.ENEMIES.keys()))
                self.fight(self.ENEMIES[enemy_name])
                
            elif choice == '2':
                self.player.enter_shop()
                
            elif choice == '3':
                if self.player.current_hp >= self.player.max_hp:
                    print("Your HP is full — you can't use a Heal Potion now.")
                else:
                    self.player.use_item('Heal Potion')

            elif choice == '4' and self.player.level >= LAST_BOSS_UNLOCK_LEVEL:
                print("\nBe ready to fight the last boss!")
                if self.fight(self.LAST_BOSS):
                    print("\nCongratulation you deafeted the last boss")
                    self.running = False
                
            elif choice == '5':
                self.save_game(self.player)
                
            elif choice == '6':
                print("\nGoodbye. Coma back soon!")
                self.running = False
                
            else:
                print("Invalid choice, choose from the menu")

    def run(self):
        self.start_menu()
        self.main_game_loop()
