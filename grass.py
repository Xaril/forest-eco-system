import organisms
import random
from earth import Earth
from water import Water
import behaviour_tree as bt
from helpers import Lerp, InverseLerp

REPRODUCTION_THRESHOLD = 60
MAX_GRASS_AMOUNT = 100
MAX_GROWTH_SPEED = 0.3 # Based on that grass takes two weeks to grow
MIN_GROWTH_SPEED = 0.2
MAX_DEGRADE_SPEED = -0.2
PLANTED_SEED_AMOUNT = -80 # With growth speed of 0.3 this will make SEED-GRASS transition take approx 10 days
REPRODUCTION_COOLDOWN = 24 # Reproduces only once a day
GRASS_WATER_CAPACITY = 1000
GRASS_WATER_USAGE = 0.1
GRASS_OPTIMAL_WATER_PERCENTAGE = 0.5 # Water percentage for fastest growth speed
GRASS_MAX_WATER_PERCENTAGE = 0.8 # Threshold when too much water starts to kill grass

class Grass(organisms.Organism):
    """Defines the grass."""
    def __init__(self, ecosystem, x, y, amount, seed=None, water_amount=None):
        super().__init__(ecosystem, organisms.Type.GRASS, x, y)
        self._amount = amount
        if seed is not None:
            self._seed = seed
        else:
            self._seed = amount <= 0

        if water_amount is not None:
            self.water_amount = water_amount
        #else:
            #elf.water_amount = random.randint(0, GRASS_WATER_CAPACITY)
        self.water_capacity = GRASS_WATER_CAPACITY
        self._hours_since_last_reproduction = random.randint(0,25)

    def get_image(self):
        if self._amount < REPRODUCTION_THRESHOLD:
            return 'images/grassLow.png'
        else:
            return 'images/grassHigh.png'


    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.Sequence()
        dead_or_alive_fallback = bt.FallBack()
        dead_or_alive_fallback.add_child(self.IsAlive(self))
        dead_or_alive_fallback.add_child(self.Die(self))

        flood_fallback = bt.FallBack()
        flood_fallback.add_child(self.IsNotFlooded(self))
        flood_fallback.add_child(self.Flood(self))

        reproduce_sequence = bt.Sequence()
        reproduce_sequence.add_child(self.CanReproduce(self))
        reproduce_sequence.add_child(self.Reproduce(self))

        tree.add_child(dead_or_alive_fallback)
        tree.add_child(flood_fallback)
        tree.add_child(self.Grow(self))
        tree.add_child(reproduce_sequence)
        return tree

    class IsAlive(bt.Condition):
        """Check if grass is alive."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._amount > 0 or (self.__outer._seed and self.__outer._amount >= PLANTED_SEED_AMOUNT )

    class Die(bt.Action):
        """Performs action after grass dies."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            earth = Earth(self.__outer._ecosystem, x, y, water_amount=self.__outer.water_amount)
            self.__outer._ecosystem.plant_map[x][y] = earth
            self._status = bt.Status.FAIL


    class IsNotFlooded(bt.Condition):
        """Check if grass is flooded."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.water_amount <= self.__outer.water_capacity

    class Flood(bt.Action):
        """Flood the grass."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            water_over = self.__outer.water_amount - self.__outer.water_capacity
            water = Water(self.__outer._ecosystem, x, y, water_over )
            self.__outer._ecosystem.water_map[x][y] = water
            self.__outer._ecosystem.plant_map[x][y] = None
            self.__outer._ecosystem.flower_map[x][y] = None
            self._status = bt.Status.FAIL


    class Grow(bt.Action):
        """Makes the tree grow."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            water_percentage = self.__outer.water_amount / self.__outer.water_capacity
            if water_percentage <= 0:
                growth_speed = MAX_DEGRADE_SPEED
            elif water_percentage <= GRASS_OPTIMAL_WATER_PERCENTAGE:
                growth_speed = Lerp(MIN_GROWTH_SPEED, MAX_GROWTH_SPEED, InverseLerp(0, GRASS_OPTIMAL_WATER_PERCENTAGE, water_percentage))
            elif water_percentage <= GRASS_MAX_WATER_PERCENTAGE:
                growth_speed = Lerp(MIN_GROWTH_SPEED, MAX_GROWTH_SPEED, 1 - InverseLerp(GRASS_OPTIMAL_WATER_PERCENTAGE,GRASS_MAX_WATER_PERCENTAGE, water_percentage))
            else:
                growth_speed = Lerp(MAX_DEGRADE_SPEED, MIN_GROWTH_SPEED, 1 - InverseLerp(GRASS_MAX_WATER_PERCENTAGE, 1, water_percentage))


            self.__outer._amount = min(MAX_GRASS_AMOUNT, self.__outer._amount + growth_speed)
            self.__outer.water_amount = max(0,self.__outer.water_amount - GRASS_WATER_USAGE )
            if self.__outer._amount > 0:
                self.__outer._seed = False
            self._status = bt.Status.SUCCESS


    class CanReproduce(bt.Condition):
        """Checks if tree is ready to reproduce."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            self.__outer._hours_since_last_reproduction += 1
            return self.__outer._amount >= REPRODUCTION_THRESHOLD and self.__outer._hours_since_last_reproduction >= REPRODUCTION_COOLDOWN

    class Reproduce(bt.Action):
        """Reproduce to adjacent cell."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):

            # Get wind information
            wind_direction, wind_speed = self.__outer._ecosystem.weather.get_wind_velocity()

            # Reproduce in direcion of the wind
            for i in range(wind_speed):
                x = self.__outer.x + (wind_direction.value[0] * (i + 1))
                y = self.__outer.y + (wind_direction.value[1] * (i + 1))

                # check if in bounds
                if x < 0 or x >= self.__outer._ecosystem.width or y < 0 or y >= self.__outer._ecosystem.height:
                    continue
                # if cell is empty or earth plant a seed
                cell = self.__outer._ecosystem.plant_map[x][y]
                if cell and cell.type == organisms.Type.EARTH and cell.water_amount > 0:
                    grass = Grass(self.__outer._ecosystem, x, y, PLANTED_SEED_AMOUNT, True, cell.water_amount)
                    self.__outer._ecosystem.plant_map[x][y] = grass
                    self.__outer._hours_since_last_reproduction = 0

            self._status = bt.Status.SUCCESS
