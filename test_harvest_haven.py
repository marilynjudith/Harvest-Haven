import unittest
import os
import harvest_haven as hh

class TestHarvestHaven(unittest.TestCase):
    def setUp(self):
        self.player = hh.Player()
        self.farm = hh.Farm()

    def test_crop_plant_and_grow(self):
        self.farm.plant(0, 0, 'Wheat')
        crop = self.farm.grid[0][0]
        self.assertEqual(crop.type, 'Wheat')
        self.assertEqual(crop.stage, 1)  # Planted
        for _ in range(hh.CROP_TYPES['Wheat']['grow_time']):
            crop.watered = hh.CROP_TYPES['Wheat']['water_needed']
            crop.fertilized = hh.CROP_TYPES['Wheat']['fertilizer_needed']
            crop.advance_day()
        self.assertEqual(crop.stage, 3)  # Harvestable

    def test_crop_death(self):
        self.farm.plant(0, 1, 'Carrot')
        crop = self.farm.grid[0][1]
        for _ in range(hh.CROP_TYPES['Carrot']['grow_time'] + 3):
            crop.advance_day()
        self.assertEqual(crop.stage, 4)  # Dead

    def test_player_inventory_and_harvest(self):
        self.player.inventory['Wheat'] = 1
        self.farm.plant(1, 1, 'Wheat')
        crop = self.farm.grid[1][1]
        crop.stage = 3  # Make harvestable
        crop.type = 'Wheat'
        crop.days_grown = hh.CROP_TYPES['Wheat']['grow_time']
        crop.watered = hh.CROP_TYPES['Wheat']['water_needed']
        crop.fertilized = hh.CROP_TYPES['Wheat']['fertilizer_needed']
        crop_type = self.farm.harvest(1, 1)
        self.player.add_harvest(crop_type)
        self.assertEqual(self.player.harvested['Wheat'], 1)
        self.assertEqual(self.player.coins, 20 + hh.CROP_TYPES['Wheat']['sell_price'])

    def test_save_and_load(self):
        self.player.inventory['Tomato'] = 2
        self.farm.plant(2, 2, 'Tomato')
        hh.save_game(self.player, self.farm, filename='test_save.json')
        loaded_player, loaded_farm = hh.load_game(filename='test_save.json')
        self.assertEqual(loaded_player.inventory['Tomato'], 2)
        self.assertEqual(loaded_farm.grid[2][2].type, 'Tomato')
        os.remove('test_save.json')

    def test_farm_display(self):
        # Just check that display runs without error
        self.farm.display()

if __name__ == '__main__':
    unittest.main() 