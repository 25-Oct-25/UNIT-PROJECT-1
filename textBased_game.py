SAVE_FILE = 'savegame.json'
LAST_BOSS_UNLOCK_LEVEL = 3

class Player:

    ROLES_INITIAL_STATS = {
        "Paladin": {"hp": 120, "atk": 15, "defense": 30, 'weapon': 'Wooden Sword'},
        "Knight":  {"hp": 140, "atk": 18, "defense": 25}, 'weapon': 'Simple Axe'
    }

    SHOP_ITEMS = {
        'Sword':    {'Price': 80,  'ATK': 10, 'defense': 5},
        'Claymore': {'Price': 150, 'ATK': 20, 'defense': 0},
        'Heal Potion': {'Price': 15, 'Effect': 50, 'Type': 'Consumable'}
    }

    def __init__(self, name: str, role: str, level: int, coins: int, inventory: dict, loaded_data = None):
        
        if loaded_data:
            self.__dict__.update(loaded_data)
        else: 
            #Name check and assign
            self.name = (name or "").strip()
            '''if not self.name:
                self.name = "Fighter"'''
            
            #role check and assign
            role = (role or "").lower().strip()
            if role not in self.ROLES_INITIAL_STATS:
                raise ValueError(f"unknown role. Choose between 1- Paladin 2- Knight")
            self.role = role

            self.level = 1
            self.xp = 0
            self.coins = 20
            self.inventory = {}
            base_stats = self.ROLES_INITIAL_STATS.get(role, self.ROLES_INITIAL_STATS[])
            self.hp = base_stats['hp']
            self.atk = base_stats['atk']
            self.defense = base_stats['def']
            self.weapon = base_stats['WEAPON']
        
            self._validate_stats()

    #Check on Stats
    def _validate_stats(self):
        s = self.stats
        if s["hp"] <= 0 or s["attack"] < 0 or s["defense"] < 0 or s["xp"] < 0:
            print("There is a problem with your stats")

    def display_stats(self):
        #print("Your current stats:")
        print(f"Stats for player {self.name}:")
        print(f"Role: {self.role}, HP: {self.hp}, Level: {self.level}")
        print(f"Attack: {self.atk}, Defense: {self.defense}")
        print(f"Coins: {self.coins}, XP: {self.xp}")
        print(f"Weapon: {self.weapon}")


    def level_up(self):
        xp_required = {1: 0, 2: 25, 3: 35, 4: 50}
        
        #to increase player level
        while self.level < 4 and self.xp >= xp_required.get(self.level + 1, float('inf')):
            self.level += 1

            #to increase player stats
            self.max_hp += 10 
            self.current_hp = self.max_hp # استعادة كاملة
            self.attack += 5
            self.defense += 3
            print(f"\nCongratulations you reached level {self.level}!")
            print(f"Your new stats: HP:{self.max_hp}, ATK:{self.atk}, DEF:{self.defense}")


    def enter_shop():
        pass
