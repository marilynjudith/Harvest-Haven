import random
import json
import os

# --- Crop Types ---
CROP_TYPES = {
    'Wheat': {'grow_time': 3, 'water_needed': 1, 'fertilizer_needed': 0, 'sell_price': 5},
    'Tomato': {'grow_time': 5, 'water_needed': 2, 'fertilizer_needed': 1, 'sell_price': 12},
    'Carrot': {'grow_time': 4, 'water_needed': 1, 'fertilizer_needed': 1, 'sell_price': 8},
}

CROP_STAGES = ['Empty', 'Planted', 'Growing', 'Harvestable', 'Dead']

# Emoji mapping for crops and stages
CROP_EMOJIS = {
    'Wheat': {
        1: '🌱',  # Planted
        2: '🌾',  # Growing
        3: '🥖',  # Harvestable (bread as a fun icon)
        4: '💀',  # Dead
    },
    'Tomato': {
        1: '🌱',
        2: '🍅',
        3: '🍅',
        4: '💀',
    },
    'Carrot': {
        1: '🌱',
        2: '🥕',
        3: '🥕',
        4: '💀',
    },
    None: {0: '⬜'}  # Empty
}

# --- Crop Class ---
class Crop:
    def __init__(self, crop_type=None):
        self.type = crop_type
        self.stage = 0  # 0: Empty, 1: Planted, 2: Growing, 3: Harvestable, 4: Dead
        self.days_grown = 0
        self.watered = 0
        self.fertilized = 0

    def plant(self, crop_type):
        self.type = crop_type
        self.stage = 1
        self.days_grown = 0
        self.watered = 0
        self.fertilized = 0

    def advance_day(self, rain=False):
        if self.stage in [0, 4]:
            return
        if rain:
            self.watered += 1
        self.days_grown += 1
        # Check for death
        if self.days_grown > CROP_TYPES[self.type]['grow_time'] + 2:
            self.stage = 4  # Dead
        # Check for harvestable
        elif self.days_grown >= CROP_TYPES[self.type]['grow_time']:
            if self.watered >= CROP_TYPES[self.type]['water_needed'] and \
               self.fertilized >= CROP_TYPES[self.type]['fertilizer_needed']:
                self.stage = 3  # Harvestable
            else:
                self.stage = 2  # Still growing
        else:
            self.stage = 2  # Growing

    def water(self):
        if self.stage in [1, 2]:
            self.watered += 1

    def fertilize(self):
        if self.stage in [1, 2]:
            self.fertilized += 1

    def harvest(self):
        if self.stage == 3:
            self.stage = 0
            crop_type = self.type
            self.type = None
            return crop_type
        return None

    def to_dict(self):
        return {
            'type': self.type,
            'stage': self.stage,
            'days_grown': self.days_grown,
            'watered': self.watered,
            'fertilized': self.fertilized
        }

    @classmethod
    def from_dict(cls, data):
        crop = cls()
        crop.type = data['type']
        crop.stage = data['stage']
        crop.days_grown = data['days_grown']
        crop.watered = data['watered']
        crop.fertilized = data['fertilized']
        return crop

# --- Farm Class ---
class Farm:
    def __init__(self, size=5):
        self.size = size
        self.grid = [[Crop() for _ in range(size)] for _ in range(size)]

    def plant(self, x, y, crop_type):
        self.grid[x][y].plant(crop_type)

    def water(self, x, y):
        self.grid[x][y].water()

    def fertilize(self, x, y):
        self.grid[x][y].fertilize()

    def harvest(self, x, y):
        return self.grid[x][y].harvest()

    def advance_day(self, rain=False):
        for row in self.grid:
            for crop in row:
                crop.advance_day(rain=rain)

    def to_dict(self):
        return {
            'size': self.size,
            'grid': [[crop.to_dict() for crop in row] for row in self.grid]
        }

    @classmethod
    def from_dict(cls, data):
        farm = cls(size=data['size'])
        for i, row in enumerate(data['grid']):
            for j, crop_data in enumerate(row):
                farm.grid[i][j] = Crop.from_dict(crop_data)
        return farm

    def display(self):
        print("\nFarm Grid:")
        for i, row in enumerate(self.grid):
            line = []
            for j, crop in enumerate(row):
                line.append(get_crop_emoji(crop))
            print(' '.join(line))

# --- Player Class ---
class Player:
    def __init__(self):
        self.energy = 10
        self.coins = 20
        self.inventory = {'Wheat': 3, 'Tomato': 1, 'Carrot': 1, 'Water': 10, 'Fertilizer': 2}
        self.harvested = {}

    def can_plant(self, crop_type):
        return self.inventory.get(crop_type, 0) > 0

    def use_seed(self, crop_type):
        if self.can_plant(crop_type):
            self.inventory[crop_type] -= 1
            return True
        return False

    def add_harvest(self, crop_type):
        self.harvested[crop_type] = self.harvested.get(crop_type, 0) + 1
        self.coins += CROP_TYPES[crop_type]['sell_price']

    def use_water(self):
        if self.inventory['Water'] > 0:
            self.inventory['Water'] -= 1
            return True
        return False

    def use_fertilizer(self):
        if self.inventory['Fertilizer'] > 0:
            self.inventory['Fertilizer'] -= 1
            return True
        return False

    def rest(self):
        self.energy = 10

    def to_dict(self):
        return {
            'energy': self.energy,
            'coins': self.coins,
            'inventory': self.inventory,
            'harvested': self.harvested
        }

    @classmethod
    def from_dict(cls, data):
        player = cls()
        player.energy = data['energy']
        player.coins = data['coins']
        player.inventory = data['inventory']
        player.harvested = data['harvested']
        return player

# --- Game Functions ---
def save_game(player, farm, filename='harvest_haven_save.json'):
    with open(filename, 'w') as f:
        json.dump({'player': player.to_dict(), 'farm': farm.to_dict()}, f)
    print('Game saved!')

def load_game(filename='harvest_haven_save.json'):
    if not os.path.exists(filename):
        print('No save file found.')
        return None, None
    with open(filename, 'r') as f:
        data = json.load(f)
    player = Player.from_dict(data['player'])
    farm = Farm.from_dict(data['farm'])
    print('Game loaded!')
    return player, farm

def get_crop_emoji(crop):
    if crop.stage == 0 or crop.type is None:
        return '⬜'
    return CROP_EMOJIS.get(crop.type, {}).get(crop.stage, '⬜')

# --- Main Game Loop ---
def main():
    print("Welcome to Harvest Haven!")
    if os.path.exists('harvest_haven_save.json'):
        choice = input('Load previous game? (y/n): ').lower()
        if choice == 'y':
            player, farm = load_game()
            if player is None:
                player, farm = Player(), Farm()
        else:
            player, farm = Player(), Farm()
    else:
        player, farm = Player(), Farm()

    day = 1
    while True:
        print(f"\n--- Day {day} ---")
        farm.display()
        print(f"Energy: {player.energy} | Coins: {player.coins}")
        print(f"Inventory: {player.inventory}")
        print(f"Harvested: {player.harvested}")
        # Random event
        event = random.choice(['none', 'rain', 'drought', 'pests'])
        if event == 'rain':
            print('It rained! All crops are watered.')
            farm.advance_day(rain=True)
        elif event == 'drought':
            print('A drought! Crops need extra water today.')
        elif event == 'pests':
            print('Pests attacked! Some crops may not grow.')
            # For simplicity, randomly kill a crop
            for _ in range(random.randint(1, 3)):
                x, y = random.randint(0, 4), random.randint(0, 4)
                if farm.grid[x][y].stage in [1, 2]:
                    farm.grid[x][y].stage = 4  # Dead
        else:
            farm.advance_day()
        # Player actions
        while player.energy > 0:
            print("\nActions: 1) Plant 2) Water 3) Fertilize 4) Harvest 5) Shop 6) Save 7) End Day 8) Quit")
            action = input("Choose action: ")
            if action == '1':
                print("Available seeds:", {k: v for k, v in player.inventory.items() if k in CROP_TYPES})
                crop_type = input("Which crop to plant? ")
                if crop_type in CROP_TYPES and player.can_plant(crop_type):
                    x, y = map(int, input("Enter grid x y (0-4 0-4): ").split())
                    if farm.grid[x][y].stage == 0:
                        farm.plant(x, y, crop_type)
                        player.use_seed(crop_type)
                        player.energy -= 1
                        print(f"Planted {crop_type} at ({x},{y})")
                    else:
                        print("That spot is not empty.")
                else:
                    print("You don't have that seed.")
            elif action == '2':
                x, y = map(int, input("Enter grid x y to water: ").split())
                if player.use_water():
                    farm.water(x, y)
                    player.energy -= 1
                    print(f"Watered crop at ({x},{y})")
                else:
                    print("No water left!")
            elif action == '3':
                x, y = map(int, input("Enter grid x y to fertilize: ").split())
                if player.use_fertilizer():
                    farm.fertilize(x, y)
                    player.energy -= 1
                    print(f"Fertilized crop at ({x},{y})")
                else:
                    print("No fertilizer left!")
            elif action == '4':
                x, y = map(int, input("Enter grid x y to harvest: ").split())
                crop_type = farm.harvest(x, y)
                if crop_type:
                    player.add_harvest(crop_type)
                    player.energy -= 1
                    print(f"Harvested {crop_type} at ({x},{y})")
                else:
                    print("Nothing to harvest there.")
            elif action == '5':
                print("Shop: 1) Wheat seed (2 coins) 2) Tomato seed (5 coins) 3) Carrot seed (3 coins) 4) Water (1 coin) 5) Fertilizer (2 coins)")
                shop_choice = input("What do you want to buy? (1-5): ")
                if shop_choice == '1' and player.coins >= 2:
                    player.inventory['Wheat'] += 1
                    player.coins -= 2
                    print("Bought Wheat seed.")
                elif shop_choice == '2' and player.coins >= 5:
                    player.inventory['Tomato'] += 1
                    player.coins -= 5
                    print("Bought Tomato seed.")
                elif shop_choice == '3' and player.coins >= 3:
                    player.inventory['Carrot'] += 1
                    player.coins -= 3
                    print("Bought Carrot seed.")
                elif shop_choice == '4' and player.coins >= 1:
                    player.inventory['Water'] += 3
                    player.coins -= 1
                    print("Bought 3 Water.")
                elif shop_choice == '5' and player.coins >= 2:
                    player.inventory['Fertilizer'] += 1
                    player.coins -= 2
                    print("Bought Fertilizer.")
                else:
                    print("Not enough coins or invalid choice.")
            elif action == '6':
                save_game(player, farm)
            elif action == '7':
                print("Ending day...")
                break
            elif action == '8':
                save_game(player, farm)
                print("Goodbye!")
                return
            else:
                print("Invalid action.")
        player.rest()
        day += 1

if __name__ == '__main__':
    main() 