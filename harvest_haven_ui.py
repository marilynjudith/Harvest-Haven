import tkinter as tk
from tkinter import messagebox, simpledialog
import harvest_haven as hh

class HarvestHavenUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Harvest Haven')
        self.player = hh.Player()
        self.farm = hh.Farm()
        self.day = 1
        self.selected_action = None
        self.create_widgets()
        self.update_ui()

    def create_widgets(self):
        # Top info
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack()
        self.day_label = tk.Label(self.info_frame, text='Day 1')
        self.day_label.pack(side=tk.LEFT, padx=10)
        self.energy_label = tk.Label(self.info_frame, text='Energy: 10')
        self.energy_label.pack(side=tk.LEFT, padx=10)
        self.coins_label = tk.Label(self.info_frame, text='Coins: 20')
        self.coins_label.pack(side=tk.LEFT, padx=10)

        # Inventory
        self.inv_frame = tk.Frame(self.root)
        self.inv_frame.pack()
        self.inv_label = tk.Label(self.inv_frame, text='Inventory:')
        self.inv_label.pack(side=tk.LEFT)
        self.inv_text = tk.Label(self.inv_frame, text='')
        self.inv_text.pack(side=tk.LEFT)

        # Farm grid
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=10, expand=True, fill=tk.BOTH)
        self.grid_buttons = []
        self.button_font = ("Arial", 28)  # Larger font for emojis
        for i in range(5):
            self.grid_frame.grid_rowconfigure(i, weight=1)
            row = []
            for j in range(5):
                self.grid_frame.grid_columnconfigure(j, weight=1)
                btn = tk.Button(self.grid_frame, text='[ ]', font=self.button_font, width=2, height=1,
                                command=lambda x=i, y=j: self.on_grid_click(x, y))
                btn.grid(row=i, column=j, padx=2, pady=2, sticky="nsew")
                row.append(btn)
            self.grid_buttons.append(row)

        # Action buttons
        self.action_frame = tk.Frame(self.root)
        self.action_frame.pack(pady=5)
        actions = [
            ('Plant', self.set_action_plant),
            ('Water', self.set_action_water),
            ('Fertilize', self.set_action_fertilize),
            ('Harvest', self.set_action_harvest),
            ('Shop', self.open_shop),
            ('Save', self.save_game),
            ('End Day', self.end_day)
        ]
        for (label, cmd) in actions:
            tk.Button(self.action_frame, text=label, width=10, command=cmd).pack(side=tk.LEFT, padx=2)

    def update_ui(self):
        self.day_label.config(text=f'Day {self.day}')
        self.energy_label.config(text=f'Energy: {self.player.energy}')
        self.coins_label.config(text=f'Coins: {self.player.coins}')
        self.inv_text.config(text=str(self.player.inventory))
        # Update grid
        for i in range(5):
            for j in range(5):
                crop = self.farm.grid[i][j]
                emoji = hh.get_crop_emoji(crop)
                self.grid_buttons[i][j].config(text=emoji)

    def set_action_plant(self):
        self.selected_action = 'plant'
        messagebox.showinfo('Action', 'Click a grid cell to plant.')

    def set_action_water(self):
        self.selected_action = 'water'
        messagebox.showinfo('Action', 'Click a grid cell to water.')

    def set_action_fertilize(self):
        self.selected_action = 'fertilize'
        messagebox.showinfo('Action', 'Click a grid cell to fertilize.')

    def set_action_harvest(self):
        self.selected_action = 'harvest'
        messagebox.showinfo('Action', 'Click a grid cell to harvest.')

    def on_grid_click(self, x, y):
        if self.selected_action == 'plant':
            self.plant_crop(x, y)
        elif self.selected_action == 'water':
            self.water_crop(x, y)
        elif self.selected_action == 'fertilize':
            self.fertilize_crop(x, y)
        elif self.selected_action == 'harvest':
            self.harvest_crop(x, y)
        self.selected_action = None
        self.update_ui()

    def plant_crop(self, x, y):
        if self.farm.grid[x][y].stage != 0:
            messagebox.showwarning('Error', 'That spot is not empty.')
            return
        # Choose crop
        seeds = {k: v for k, v in self.player.inventory.items() if k in hh.CROP_TYPES and v > 0}
        if not seeds:
            messagebox.showwarning('Error', 'No seeds available!')
            return
        crop_type = simpledialog.askstring('Plant', f'Which crop? {list(seeds.keys())}')
        if crop_type not in seeds:
            messagebox.showwarning('Error', 'Invalid crop type.')
            return
        self.farm.plant(x, y, crop_type)
        self.player.use_seed(crop_type)
        self.player.energy -= 1
        messagebox.showinfo('Planted', f'Planted {crop_type} at ({x},{y})')

    def water_crop(self, x, y):
        if self.player.use_water():
            self.farm.water(x, y)
            self.player.energy -= 1
            messagebox.showinfo('Watered', f'Watered crop at ({x},{y})')
        else:
            messagebox.showwarning('Error', 'No water left!')

    def fertilize_crop(self, x, y):
        if self.player.use_fertilizer():
            self.farm.fertilize(x, y)
            self.player.energy -= 1
            messagebox.showinfo('Fertilized', f'Fertilized crop at ({x},{y})')
        else:
            messagebox.showwarning('Error', 'No fertilizer left!')

    def harvest_crop(self, x, y):
        crop_type = self.farm.harvest(x, y)
        if crop_type:
            self.player.add_harvest(crop_type)
            self.player.energy -= 1
            messagebox.showinfo('Harvested', f'Harvested {crop_type} at ({x},{y})')
        else:
            messagebox.showwarning('Error', 'Nothing to harvest there.')

    def open_shop(self):
        shop_items = [
            ('Wheat', 2),
            ('Tomato', 5),
            ('Carrot', 3),
            ('Water', 1),
            ('Fertilizer', 2)
        ]
        shop_str = '\n'.join([f'{i+1}) {name} ({price} coins)' for i, (name, price) in enumerate(shop_items)])
        choice = simpledialog.askinteger('Shop', f'What do you want to buy?\n{shop_str}')
        if not choice or choice < 1 or choice > len(shop_items):
            return
        name, price = shop_items[choice-1]
        if self.player.coins < price:
            messagebox.showwarning('Error', 'Not enough coins!')
            return
        if name == 'Water':
            self.player.inventory['Water'] += 3
        else:
            self.player.inventory[name] = self.player.inventory.get(name, 0) + 1
        self.player.coins -= price
        messagebox.showinfo('Shop', f'Bought {name}!')
        self.update_ui()

    def save_game(self):
        hh.save_game(self.player, self.farm)
        messagebox.showinfo('Save', 'Game saved!')

    def end_day(self):
        # Random event
        import random
        event = random.choice(['none', 'rain', 'drought', 'pests'])
        if event == 'rain':
            messagebox.showinfo('Event', 'It rained! All crops are watered.')
            self.farm.advance_day(rain=True)
        elif event == 'drought':
            messagebox.showinfo('Event', 'A drought! Crops need extra water today.')
        elif event == 'pests':
            messagebox.showinfo('Event', 'Pests attacked! Some crops may not grow.')
            for _ in range(random.randint(1, 3)):
                x, y = random.randint(0, 4), random.randint(0, 4)
                if self.farm.grid[x][y].stage in [1, 2]:
                    self.farm.grid[x][y].stage = 4  # Dead
        else:
            self.farm.advance_day()
        self.player.rest()
        self.day += 1
        self.update_ui()

if __name__ == '__main__':
    root = tk.Tk()
    app = HarvestHavenUI(root)
    root.mainloop() 