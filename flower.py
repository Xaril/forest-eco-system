import organisms
import behaviour_tree as bt
from helpers import Lerp, InverseLerp

REPRODUCTION_THRESHOLD = 60 # Amout of flower needed to be able to reproduce
MAX_GROWTH_SPEED = 0.15 # Based on that FLOWER takes around five weeks to grow
MIN_GROWTH_SPEED = 0.5
PLANTED_SEED_AMOUNT = -50 # With growth speed of 0.1 this will make SEED-FLOWER transition take approx 3 weeks
MAX_FLOWER_AMOUNT = 100
FLOWER_WATER_USAGE = 0.2
FLOWER_OPTIMAL_WATER_PERCENTAGE = 0.5 # Water percentage for fastest growth speed
FLOWER_MAX_WATER_PERCENTAGE = 0.8 # Threshold when too much water starts to kill FLOWER
MAX_DEGRADE_SPEED = -0.1

class Flower(organisms.Organism):
    """Defines the flower."""
    def __init__(self, ecosystem, x, y, amount, seed=None):
        super().__init__(ecosystem, organisms.Type.FLOWER, x, y)
        if seed:
            self._seed = seed
        else:
            self._seed = amount <= 0
        self._amount = amount

    def get_image(self):
        if self._seed:
            return 'images/flowerSeed.png'
        else:
            return 'images/flower.png'


    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.Sequence()
        dead_or_alive_fallback = bt.FallBack()
        dead_or_alive_fallback.add_child(self.IsAlive(self))
        dead_or_alive_fallback.add_child(self.Die(self))

        tree.add_child(dead_or_alive_fallback)
        tree.add_child(self.Grow(self))
        return tree


    class IsAlive(bt.Condition):
        """Check if flower is alive."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._amount > 0 or (self.__outer._seed and self.__outer._amount >= PLANTED_SEED_AMOUNT )

    class Die(bt.Action):
        """Performs action after flower dies."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            self.__outer._ecosystem.flower_map[x][y] = None
            self._status = bt.Status.FAIL


    class Grow(bt.Action):
        """Makes the tree grow."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            # get water info from groud organism (earth or grass)
            water_amount = self.__outer._ecosystem.plant_map[x][y].water_amount
            water_capacity = self.__outer._ecosystem.plant_map[x][y].water_capacity
            water_percentage = water_amount / water_capacity
            if water_percentage <= 0:
                growth_speed = MAX_DEGRADE_SPEED
            elif water_percentage <= FLOWER_OPTIMAL_WATER_PERCENTAGE:
                growth_speed = Lerp(MIN_GROWTH_SPEED, MAX_GROWTH_SPEED, InverseLerp(0, FLOWER_OPTIMAL_WATER_PERCENTAGE, water_percentage))
            elif water_percentage <= FLOWER_MAX_WATER_PERCENTAGE:
                growth_speed = Lerp(MIN_GROWTH_SPEED, MAX_GROWTH_SPEED, 1 - InverseLerp(FLOWER_OPTIMAL_WATER_PERCENTAGE,FLOWER_MAX_WATER_PERCENTAGE, water_percentage))
            else:
                growth_speed = Lerp(MAX_DEGRADE_SPEED, MIN_GROWTH_SPEED, 1 - InverseLerp(FLOWER_MAX_WATER_PERCENTAGE, 1, water_percentage))


            self.__outer._amount = min(MAX_FLOWER_AMOUNT, self.__outer._amount + growth_speed)
            self.__outer._ecosystem.plant_map[x][y].water_amount = max(0, self.__outer._ecosystem.plant_map[x][y].water_amount - FLOWER_WATER_USAGE)
            if self.__outer._amount > 0:
                self.__outer._seed = False
            self._status = bt.Status.SUCCESS
