import organisms
from water import Water
import behaviour_tree as bt
import random

EARTH_WATER_CAPACITY = 1000

class Earth(organisms.Organism):
    """Defines the earth."""
    def __init__(self, ecosystem, x, y, water_amount=None):
        super().__init__(ecosystem, organisms.Type.EARTH, x, y)
        self._water_capacity = EARTH_WATER_CAPACITY
        if water_amount:
            self.water_amount = water_amount
        else:
            self.water_amount = random.randint(0, EARTH_WATER_CAPACITY)
    def get_image(self):
        return 'images/earth.png'

    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.FallBack()

        flood_fallback = bt.FallBack()
        flood_fallback.add_child(self.IsNotFlooded(self))
        flood_fallback.add_child(self.Flood(self))

        tree.add_child(flood_fallback)
        return tree

    class IsNotFlooded(bt.Condition):
        """Check if earth is flooded."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.water_amount <= self.__outer._water_capacity

    class Flood(bt.Action):
        """Flood the earth."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            water_over = self.__outer.water_amount - self.__outer._water_capacity
            water = Water(self.__outer._ecosystem, x, y, water_over)
            self.__outer._ecosystem.water_map[x][y] = water
            self.__outer._ecosystem.plant_map[x][y] = None
            self.__outer._ecosystem.flower_map[x][y] = None
            self._status = bt.Status.FAIL
