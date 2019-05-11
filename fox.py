import organisms
import behaviour_tree as bt
import helpers
import random
import math
from astar import astar
from water import WATER_POOL_CAPACITY

HUNGER_SEEK_THRESHOLD = 50
THIRST_SEEK_THRESHOLD = 50
TIRED_SEEK_THRESHOLD = 50
HUNGER_DAMAGE_THRESHOLD = 75
THIRST_DAMAGE_THRESHOLD = 85
TIRED_DAMAGE_THRESHOLD = 80
HUNGER_DAMAGE_FACTOR = 0.2
THIRST_DAMAGE_FACTOR = 0.3
TIRED_DAMAGE_FACTOR = 0.1
RABBIT_HUNGER_SATISFACTION = 100
RABBIT_SIZE_FACTOR = 1/20
WATER_DRINKING_AMOUNT = 0.00001 * WATER_POOL_CAPACITY

EATING_AND_DRINKING_SLEEP_FACTOR = 0.3
SLEEP_TIME = 8

HEAL_AMOUNT = 4

REPRODUCTION_TIME = 24*30 # Rabbits are pregnant for 30 days
REPRODUCTION_COOLDOWN = 24*5 # Rabbits usually have to wait 5 days before being able to reproduce again
NEW_BORN_TIME = 24*30
NURSE_COOLDOWN = 24

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
        tree.add_child(self.ReduceReproductionTimer(self))
        tree.add_child(self.DenMovement(self))
        tree.add_child(self.IncreaseHunger(self))
        tree.add_child(self.IncreaseThirst(self))
        tree.add_child(self.ChangeTired(self))
        tree.add_child(self.HandleNursing(self))
        tree.add_child(self.IncreaseAge(self))
        tree.add_child(self.TakeDamage(self))
        tree.add_child(self.ReplenishHealth(self))

        # Logic for the fox
        logic_fallback = bt.FallBack()
        tree.add_child(logic_fallback)

        # Dying
        die_sequence = bt.Sequence()
        logic_fallback.add_child(die_sequence)
        die_sequence.add_child(self.Dying(self))
        die_sequence.add_child(self.Die(self))

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

    class ReduceReproductionTimer(bt.Action):
        """Ticks down the reproduction timer for the fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer.reproduction_timer = max(0, self.__outer.reproduction_timer - 1)
            if self.__outer.reproduction_timer == 0 and self.__outer._adult:
                self.__outer.can_reproduce = True
            self._status = bt.Status.SUCCESS

    class DenMovement(bt.Action):
        """Updates whether the fox is in its den or not."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            den = self.__outer.den

            if den is None:
                self.__outer.in_den = False
            else:
                self.__outer.in_den = (x == den.x and y == den.y)
            self._status = bt.Status.SUCCESS

    class IncreaseHunger(bt.Action):
        """Increases the fox's hunger."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            factor = 1 if not self.__outer._asleep else EATING_AND_DRINKING_SLEEP_FACTOR
            if not self.__outer._stabilized_health:
                self.__outer._hunger += factor * self.__outer._hunger_speed
            self._status = bt.Status.SUCCESS

    class IncreaseThirst(bt.Action):
        """Increases the fox's thirst."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            factor = 1 if not self.__outer._asleep else EATING_AND_DRINKING_SLEEP_FACTOR
            if not self.__outer._stabilized_health:
                self.__outer._thirst += factor * self.__outer._thirst_speed
            self._status = bt.Status.SUCCESS

    class ChangeTired(bt.Action):
        """Changes the fox's tiredness depending on if it is awake."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            if not self.__outer._asleep:
                if not self.__outer._stabilized_health:
                    self.__outer._tired += self.__outer._tired_speed
            else:
                self.__outer._tired = max(0, self.__outer._tired - TIRED_DAMAGE_THRESHOLD / SLEEP_TIME)
                self.__outer._sleep_time += 1
            self._status = bt.Status.SUCCESS

    class HandleNursing(bt.Action):
        """Handles nursing variables."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            if self.__outer.female:
                if self.__outer._stop_nursing_timer > 0:
                    self.__outer._stop_nursing_timer = max(0, self.__outer._stop_nursing_timer - 1)
                    self.__outer._nurse_timer = max(0, self.__outer._nurse_timer - 1)
            self._status = bt.Status.SUCCESS

    class IncreaseAge(bt.Action):
        """Increases the fox's age."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer.age += 1
            adult_age = 24*300

            # Become adults
            if not self.__outer._adult and self.__outer.age >= adult_age:
                self.__outer._adult = True
                self.__outer.can_reproduce = True
                self.__outer.size = self.__outer._max_size
                self.__outer._vision_range = self.__outer._max_vision_range
                self.__outer._movement_cooldown = self.__outer._min_movement_cooldown

            # Lerp values depending on age
            if not self.__outer._adult:
                self.__outer.size = helpers.Lerp(0, self.__outer._max_size, self.__outer.age / (adult_age))
                for key in self.__outer._vision_range:
                    self.__outer._vision_range[key] = min(self.__outer._max_vision_range[key], helpers.Lerp(0, self.__outer._max_vision_range[key], self.__outer.age / (NEW_BORN_TIME)))
                self.__outer._movement_cooldown = helpers.Lerp(2 * self.__outer._min_movement_cooldown, self.__outer._min_movement_cooldown, self.__outer.age / (adult_age))


            self._status = bt.Status.SUCCESS

    class TakeDamage(bt.Action):
        """Take damage from various sources."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self._status = bt.Status.SUCCESS

            # Hunger
            hunger = self.__outer._hunger
            if hunger >= HUNGER_DAMAGE_THRESHOLD:
                self.__outer._health -= (hunger - HUNGER_DAMAGE_THRESHOLD) * HUNGER_DAMAGE_FACTOR

            # Thirst
            thirst = self.__outer._thirst
            if thirst >= THIRST_DAMAGE_THRESHOLD:
                self.__outer._thirst -= (thirst - THIRST_DAMAGE_THRESHOLD) * THIRST_DAMAGE_FACTOR

            # Tiredness
            tired = self.__outer._tired
            if tired >= TIRED_DAMAGE_THRESHOLD:
                self.__outer._tired -= (tired - TIRED_DAMAGE_THRESHOLD) * TIRED_DAMAGE_FACTOR

    class ReplenishHealth(bt.Action):
        """Replenish health if in a healthy condition."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self._status = bt.Status.SUCCESS

            hunger = self.__outer._hunger
            thirst = self.__outer._thirst
            tired = self.__outer._tired

            if hunger < HUNGER_SEEK_THRESHOLD and thirst < THIRST_SEEK_THRESHOLD and tired < TIRED_SEEK_THRESHOLD and self.__outer._health > 0:
                self.__outer._health += HEAL_AMOUNT

    #########
    # DYING #
    #########

    class Dying(bt.Condition):
        """Check if the fox is dying."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._health <= 0 or self.__outer.age >= self.__outer._life_span

    class Die(bt.Action):
        """Kill the fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
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
