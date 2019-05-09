import organisms
import behaviour_tree as bt
import constants
from helpers import Lerp, InverseLerp, Direction

REPRODUCTION_THRESHOLD = 60 # Amout of flower needed to be able to reproduce
MAX_GROWTH_SPEED = 0.15 # Based on that FLOWER takes around five weeks to grow
MIN_GROWTH_SPEED = 0.05
PLANTED_SEED_AMOUNT = -50 # With growth speed of 0.1 this will make SEED-FLOWER transition take approx 3 weeks
MAX_FLOWER_AMOUNT = 100
FLOWER_WATER_USAGE = 0.2
FLOWER_OPTIMAL_WATER_PERCENTAGE = 0.5 # Water percentage for fastest growth speed
FLOWER_MAX_WATER_PERCENTAGE = 0.8 # Threshold when too much water starts to kill FLOWER
MAX_DEGRADE_SPEED = -0.1
MAX_NECTAR_AMOUNT_MULTIPLIER = 0.5 # the max amount of nectar depents on flower amount
NECTAR_WATER_USAGE = 0.1
NECTAR_PRODUCTION_SPEED = 0.1

class Flower(organisms.Organism):
    """Defines the flower."""
    def __init__(self, ecosystem, x, y, amount, seed=False, nectar=0):
        super().__init__(ecosystem, organisms.Type.FLOWER, x, y)
        if seed:
            self.seed = seed
        else:
            self.seed = amount <= 0
        self._amount = amount
        self.nectar = nectar
        self.has_seed = False

    def get_image(self):
        if self.seed:
            return 'images/flowerSeed.png'
        else:
            return 'images/flower.png'


    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.FallBack()

        # check if dead
        dead_or_alive_sequence = bt.Sequence()
        dead_or_alive_sequence.add_child(self.IsDead(self))
        dead_or_alive_sequence.add_child(self.Die(self))

        # things can happen always
        sequence = bt.Sequence()
        sequence.add_child(self.Grow(self))
        nectar_production = bt.Sequence()
        nectar_production.add_child(self.CanProduceNectar(self))
        nectar_production.add_child(self.ProduceNectar(self))
        sequence.add_child(nectar_production)

        # logic
        logic_fallback = bt.FallBack()

        tree.add_child(dead_or_alive_sequence)
        tree.add_child(sequence)
        tree.add_child(logic_fallback)
        return tree


    class IsDead(bt.Condition):
        """Check if flower is alive."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            isFlowerDead = self.__outer._amount < 0 or (self.__outer.seed and self.__outer._amount < PLANTED_SEED_AMOUNT)
            isGroundDead = self.__outer._ecosystem.plant_map[self.__outer.x][self.__outer.y] == None # Check if there is grass or ground under. Could be flooded
            isTree = not isGroundDead and self.__outer._ecosystem.plant_map[self.__outer.x][self.__outer.y].type == organisms.Type.TREE
            return isFlowerDead or isGroundDead or isTree

    class Die(bt.Action):
        """Performs action after flower dies."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            self.__outer._ecosystem.flower_map[x][y].remove(self.__outer)
            self._status = bt.Status.SUCCESS


    class Grow(bt.Action):
        """Makes the flower grow."""
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
                self.__outer.seed = False
            self._status = bt.Status.SUCCESS


    class CanProduceNectar(bt.Condition):
        """Check if flower can produce nectar."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            is_big_enough = self.__outer._amount > REPRODUCTION_THRESHOLD
            have_enough_water = self.__outer._ecosystem.plant_map[x][y].water_amount >= NECTAR_WATER_USAGE
            have_room_for_more_nectar = self.__outer.nectar < self.__outer._amount * MAX_NECTAR_AMOUNT_MULTIPLIER
            return is_big_enough and have_enough_water and have_room_for_more_nectar

    class ProduceNectar(bt.Action):
        """Performs action after flower dies."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            self.__outer.nectar = min(self.__outer._amount * MAX_NECTAR_AMOUNT_MULTIPLIER, self.__outer.nectar + NECTAR_PRODUCTION_SPEED)
            self.__outer._ecosystem.plant_map[x][y].water_amount = max(0, self.__outer._ecosystem.plant_map[x][y].water_amount - NECTAR_WATER_USAGE)
            # Update nectar smell map
            self.__outer._ecosystem.nectar_smell_map[x][y] += self.__outer.nectar
            wind_direction, wind_speed = self.__outer._ecosystem.weather.get_wind_velocity()
            # TODO: make wind affect spreding of the smell
            for i in range(0, constants.NECTAR_SMELL_RANGE):
                for dir in list(Direction):
                    new_x = x + (dir.value[0] * (i + 1))
                    new_y = y + (dir.value[1] * (i + 1))
                    # check if in bounds
                    if new_x < 0 or new_x >= self.__outer._ecosystem.width or new_y < 0 or new_y >= self.__outer._ecosystem.height:
                        continue
                    self.__outer._ecosystem.nectar_smell_map[new_x][new_y] += self.__outer.nectar/(i+1)

            self._status = bt.Status.SUCCESS
