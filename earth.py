import organisms
from water import Water
import behaviour_tree as bt

EARTH_WATER_CAPACITY = 1000
EARTH_FLOOD_MULTIPLIER = 1.5

class Earth(organisms.Organism):
    """Defines the earth."""
    def __init__(self, ecosystem, x, y, water_amount=EARTH_WATER_CAPACITY):
        super().__init__(ecosystem, organisms.Type.EARTH, x, y)
        self._water_capacity = EARTH_WATER_CAPACITY
        self._water_amount = water_amount

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
            return self.__outer._water_amount < self.__outer._water_capacity * EARTH_FLOOD_MULTIPLIER

    class Flood(bt.Action):
        """Flood the earth."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            water = Water(self.__outer._ecosystem, x, y)
            self.__outer._ecosystem.water_map[x][y] = water
            self.__outer._ecosystem.plant_map[x][y] = None
            self.__outer._ecosystem.flower_map[x][y] = None
            self._status = bt.Status.FAIL
