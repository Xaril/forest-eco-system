import organisms
import behaviour_tree as bt
import helpers
import random
import math
from astar import astar
from water import WATER_POOL_CAPACITY

class Fox(organisms.Organism):
    """Defines the fox."""
    def __init__(self, ecosystem, x, y, female, adult=False, hunger=0,
                 thirst=0, tired=0, health=100, size=35, life_span=24*365*5,
                 hunger_speed=50/36, thirst_speed=50/72, tired_speed=50/36,
                 vision_range={'left': 4, 'right': 4, 'up': 4, 'down': 4},
                 den=None, in_den=False, movement_cooldown=2, age=0):
        super().__init__(ecosystem, organisms.Type.FOX, x, y)
        self.female = female
        self._adult = adult

        self._hunger = hunger
        self._thirst = thirst
        self._tired = tired
        self._health = health
        self._life_span = life_span
        self.age = age
        self._hunger_speed = hunger_speed
        self._thirst_speed = thirst_speed
        self._tired_speed = tired_speed
        self._needs_to_poop = False
        self._poop_contains_seed = False

        if self._adult:
            self.size = size
            self._max_size = size
            self._vision_range = vision_range
            self._max_vision_range = vision_range
        else:
            self.size = 1
            self._max_size = size
            self._vision_range = {
                'left': 0,
                'right': 0,
                'up': 0,
                'down': 0
            }
            self._max_vision_range = vision_range


        # TODO:
        #     * Genetic variables

        self.can_reproduce = self._adult
        self.pregnant = False
        self.partner = None
        self.reproduction_timer = 0
        self._stabilized_health = False
        self._nurse_timer = 0
        self._stop_nursing_timer = 0

        self.den = den
        self.in_den = False

        self._asleep = False
        self._sleep_time = 0

        if self._adult:
            self._movement_cooldown = movement_cooldown
            self._min_movement_cooldown = movement_cooldown
        else:
            self._movement_cooldown = 2 * movement_cooldown
            self._min_movement_cooldown = movement_cooldown

        self._movement_timer = self._movement_cooldown
        self._movement_path = None


    def get_image(self):
        if self._adult:
            return 'images/foxAdult.png'
        else:
            return 'images/foxYoung.png'


    def generate_tree(self):
        """Generates the tree for the fox."""
        tree = bt.Sequence()
        tree.add_child(self.ReduceMovementTimer(self))

        # Logic for the fox
        logic_fallback = bt.FallBack()
        tree.add_child(logic_fallback)

        # Moving randomly
        random_movement_sequence = bt.Sequence()
        logic_fallback.add_child(random_movement_sequence)
        random_movement_sequence.add_child(self.CanMove(self))
        random_movement_sequence.add_child(self.MoveRandomly(self))

        return tree

    #####################
    # VARIABLE CONTROLS #
    #####################

    class ReduceMovementTimer(bt.Action):
        """Ticks down the movement timer for the fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._movement_timer = max(0, self.__outer._movement_timer - 1)
            self._status = bt.Status.SUCCESS

    class CanMove(bt.Condition):
        """Check if the fox can move."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._movement_timer == 0

    ###################
    # RANDOM MOVEMENT #
    ###################

    class MoveRandomly(bt.Action):
        """Moves the fox randomly."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            # TODO: Make excessive movement result in size decrease?
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem
            direction = random.choice(list(helpers.Direction))
            dx = direction.value[0]
            dy = direction.value[1]

            if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                self._status = bt.Status.FAIL
            elif ecosystem.water_map[x + dx][y + dy]:
                self._status = bt.Status.FAIL
            elif ecosystem.animal_map[x + dx][y + dy]:
                occupied_space = 0
                if ecosystem.plant_map[x + dx][y + dy] and ecosystem.plant_map[x + dx][y + dy].type == organisms.Type.TREE:
                    occupied_space += 50
                for animal in ecosystem.animal_map[x + dx][y + dy]:
                    occupied_space += animal.size
                from ecosystem import ANIMAL_CELL_CAPACITY
                if occupied_space + self.__outer.size > ANIMAL_CELL_CAPACITY:
                    self._status = bt.Status.FAIL
            else:
                self._status = bt.Status.SUCCESS
                self.__outer._movement_timer += self.__outer._movement_cooldown
                index = ecosystem.animal_map[x][y].index(self.__outer)
                ecosystem.animal_map[x + dx][y + dy].append(ecosystem.animal_map[x][y].pop(index))
                self.__outer.x += dx
                self.__outer.y += dy
