import organisms
from water import Water
import behaviour_tree as bt
import random
import constants
from helpers import Direction

EARTH_WATER_CAPACITY = 1000

class Earth(organisms.Organism):
    """Defines the earth."""
    def __init__(self, ecosystem, x, y, water_amount=None):
        super().__init__(ecosystem, organisms.Type.EARTH, x, y)
        self.water_capacity = EARTH_WATER_CAPACITY
        if water_amount is not None:
            self.water_amount = water_amount
        else:
            self.water_amount = random.randint(0, EARTH_WATER_CAPACITY)
    def get_image(self):
        return 'images/earth.png'

    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.Sequence()

        flood_fallback = bt.FallBack()
        flood_fallback.add_child(self.IsNotFlooded(self))
        flood_fallback.add_child(self.Flood(self))

        tree.add_child(flood_fallback)
        tree.add_child(self.MoveWater(self))
        return tree

    class IsNotFlooded(bt.Condition):
        """Check if earth is flooded."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.water_amount <= self.__outer.water_capacity

    class Flood(bt.Action):
        """Flood the earth."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            water_over = self.__outer.water_amount - self.__outer.water_capacity
            water = Water(self.__outer._ecosystem, x, y, water_over)
            self.__outer._ecosystem.water_map[x][y] = water
            self.__outer._ecosystem.plant_map[x][y] = None
            self.__outer._ecosystem.flower_map[x][y].clear()
            self._status = bt.Status.FAIL


    class MoveWater(bt.Action):
        """Simulater subterranean water movements"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            directions = list(Direction)
            min_water_cell = self.__outer
            for dir in directions:
                x = self.__outer.x + dir.value[0]
                y = self.__outer.y + dir.value[1]

                # check if in bounds
                if x < 0 or x >= self.__outer._ecosystem.width or y < 0 or y >= self.__outer._ecosystem.height:
                    continue

                cell = self.__outer._ecosystem.plant_map[x][y]
                if not cell or cell.type == organisms.Type.TREE:
                    continue
                if cell.water_amount < min_water_cell.water_amount:
                    min_water_cell = cell


            water_diff = (self.__outer.water_amount - min_water_cell.water_amount) / 2
            if min_water_cell.type == organisms.Type.EARTH:
                moved_water = water_diff  * constants.EARTH_TO_EARTH_WATER_MOVE_SPEED
            elif min_water_cell.type == organisms.Type.GRASS:
                moved_water = water_diff  * constants.EARTH_TO_GRASS_WATER_MOVE_SPEED

            self.__outer.water_amount -= moved_water
            min_water_cell.water_amount += moved_water
