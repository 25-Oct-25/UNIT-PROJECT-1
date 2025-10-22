SAVE_FILE = 'savegame.json'
LAST_BOSS_UNLOCK_LEVEL = 3

class Player:

    ROLES_INITIAL_STATS = {
        "Paladin": {"HP": 120, "ATK": 15, "DEFENSE": 2, 'COINS': 20, 'WEAPON': 'Wooden Sword'},
        "Knight":  {"HP": 140, "ATK": 18, "DEFENSE": 1, 'COINS': 20, 'WEAPON': 'Simple Axe'}
    }

    SHOP_ITEMS = {
        'Sword': {'Price': 60,  'ATK': 10, 'DEFENSE': 5, 'Type': 'Weapon'},
        'Claymore': {'Price': 80, 'ATK': 20, 'DEFENSE': 0, 'Type': 'Weapon'},
        'Heal Potion': {'Price': 20, 'Effect': 10, 'Type': 'Consumable'}
    }

    def __init__(self, name: str = "", role: str = "", loaded_data = None):
        
        if loaded_data:
            self.__dict__.update(loaded_data)
        else: 
            #Name check and assign
            self.name = (name or "").strip()
            
            #role check and assign
            role = (role or "").strip()
            if role not in self.ROLES_INITIAL_STATS:
                raise ValueError(f"unknown role. Choose between 1 and 2")
            self.role = role

            self.level = 1
            self.xp = 0
            self.inventory = {}
            base_stats = self.ROLES_INITIAL_STATS.get(role, self.ROLES_INITIAL_STATS)
            self.max_hp = base_stats['HP']
            self.current_hp = base_stats['HP']
            self.atk = base_stats['ATK']
            self.defense = base_stats['DEFENSE']
            self.coins = base_stats['COINS']
            self.weapon = base_stats['WEAPON']
        
    def display_stats(self):
        print("\nYour current stats:")
        print(f"Role: {self.role}, HP: {self.current_hp} / {self.max_hp}, Level: {self.level}")
        print(f"ATK: {self.atk}, DEF: {self.defense}")
        print(f"Coins: {self.coins}, XP: {self.xp}")
        print(f"Weapon: {self.weapon}")


    def level_up(self):
        xp_required = {1: 0, 2: 25, 3: 35, 4: 50}
        
        #to increase player level
        while self.level < 4 and self.xp >= xp_required.get(self.level + 1, float('inf')):
            self.level += 1

            #to increase player stats
            self.max_hp += 10 
            self.current_hp = self.max_hp
            self.atk += 5
            self.defense += 3
            print(f"\nCongratulations you reached level {self.level}!")
            print(f"Your new stats: HP:{self.max_hp}, ATK:{self.atk}, DEF:{self.defense}")


    def use_item(self, item_name):

        if item_name in self.inventory and self.inventory[item_name] > 0:
            
            if item_name not in self.SHOP_ITEMS:
                print(f"{item_name} is unknown.")
                return
            
            item_stats = self.SHOP_ITEMS[item_name]
            
            if item_name == 'Heal Potion':
                heal_amount = item_stats['Effect']
                heal_final = min(heal_amount, self.max_hp - self.current_hp)
                
                if heal_final > 0:
                    self.current_hp += heal_final
                    self.inventory[item_name] -= 1
                    print(f"You used {item_name} and healed {heal_final} HP. Your current HP is: {self.current_hp}")
                else:
                    print("Your HP is full")
        else:
            print(f"No {item_name} in your inventory")


    def enter_shop(self):

        print(f"\nWelcome in the shop, currently you have {self.coins} coins.")
        
        items_list = list(self.SHOP_ITEMS.items())
        
        print("-" * 35)
        print("Available items: ")
        
        #items list
        for i, (name, stats) in enumerate(items_list):
            details = f"ATK+{stats['ATK']}, DEF+{stats['DEFENSE']}" if stats['Type'] == 'Weapon' else f"Heals {stats['Effect']} HP"
            print(f"  {i+1}. {name} (Price: {stats['Price']} | Stats: {details})")

        print(f"  {len(items_list) + 1}. using heal potion (You have: {self.inventory.get('Heal Potion', 0)})")
        print(f"  {len(items_list) + 2}. Exit")
        print("-" * 35)

        while True:
            choice = input("Enter number to use or exit: ")
            
            try:
                choice = int(choice)
                
                if choice == len(items_list) + 2:
                    print("Exiting Shop...")
                    break
                
                elif choice == len(items_list) + 1:
                    self.use_item('Heal Potion')
                    continue
                    
                elif 1 <= choice <= len(items_list):
                    item_name, item_stats = items_list[choice - 1]
                    
                    if self.coins >= item_stats['Price']:
                        self.coins -= item_stats['Price']
                        print(f"You bought {item_name}  price: {item_stats['Price']} coins. You have {self.coins} coins left.")

                        if item_stats['Type'] == 'Weapon':

                            self.atk += item_stats['ATK']
                            self.defense += item_stats['DEFENSE']
                            self.weapon = item_name
                            print(f"{item_name} is ready. Your stats changed")
                        else: 
                            #Consumable (Potion)
                            self.inventory[item_name] = self.inventory.get(item_name, 0) + 1
                            
                    else:
                        print("No enough coins to buy this item.")
                else:
                    print("Not a valid choice")
            except ValueError:
                print("Please enter a valid number")

