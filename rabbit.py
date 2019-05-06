import organisms
import behaviour_tree as bt
import helpers
import random
from grass import MAX_GRASS_AMOUNT

HUNGER_SEEK_THRESHOLD = 50
THIRST_SEEK_THRESHOLD = 50
TIRED_SEEK_THRESHOLD = 50
HUNGER_DAMAGE_THRESHOLD = 75
THIRST_DAMAGE_THRESHOLD = 85
TIRED_DAMAGE_THRESHOLD = 80
HUNGER_DAMAGE_FACTOR = 0.5
FLOWER_HUNGER_SATISFACTION = 45
GRASS_HUNGER_SATISFACTION = 20
GRASS_EATING_AMOUNT = 0.2 * MAX_GRASS_AMOUNT

HEAL_AMOUNT = 4

REPRODUCTION_TIME = 24*30 # Rabbits are pregnant for 30 days
REPRODUCTION_COOLDOWN = 24*5 # Rabbits usually have to wait 5 days before being able to reproduce again


class Rabbit(organisms.Organism):
    """Defines the rabbit."""
    def __init__(self, ecosystem, x, y, female, adult=False, hunger=0,
                 thirst=0, tired=0, health=100, size=20, life_span=24*365*7,
                 hunger_speed=50/12, thirst_speed=50/24, tired_speed=50/12,
                 vision_range=50, burrow=None, in_burrow=False,
                 movement_cooldown=3):
        super().__init__(ecosystem, organisms.Type.RABBIT, x, y)
        self._female = female
        self._adult = adult

        self._hunger = hunger
        self._thirst = thirst
        self._tired = tired
        self._health = health
        self.size = size
        self._life_span = life_span
        self._hunger_speed = hunger_speed
        self._thirst_speed = thirst_speed
        self._tired_speed = tired_speed
        self._vision_range = vision_range

        # TODO:
        #     * Genetic variables
        #     * Pooping

        self._can_reproduce = self._adult
        self._pregnant = False
        self._partner = None

        self._burrow = burrow
        self._in_burrow = False

        self._movement_cooldown = movement_cooldown
        self._movement_timer = 3


    def get_image(self):
        if self._adult:
            return 'images/rabbitAdult.png'
        else:
            return 'images/rabbitYoung.png'


    def generate_tree(self):
        """Generates the tree for the rabbit."""
        tree = bt.Sequence()
        tree.add_child(self.ReduceMovementTimer(self))
        tree.add_child(self.IncreaseHunger(self))
        tree.add_child(self.TakeDamage(self))
        tree.add_child(self.ReplenishHealth(self))

        logic_fallback = bt.FallBack()
        tree.add_child(logic_fallback)
        # Sleeping

        # Dying

        # Avoiding enemies

        # Eating
        hungry_sequence = bt.Sequence()
        logic_fallback.add_child(hungry_sequence)
        hungry_sequence.add_child(self.Hungry(self))

        hungry_fallback = bt.FallBack()
        hungry_sequence.add_child(hungry_fallback)

        adjacent_food_sequence = bt.Sequence()
        hungry_fallback.add_child(adjacent_food_sequence)
        adjacent_food_sequence.add_child(self.FoodAdjacent(self))
        adjacent_food_sequence.add_child(self.Eat(self))


        # Drinking

        # Pooping

        # Sleeping

        # Giving birth

        # Reproducing

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
        """Ticks down the movement timer for the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._movement_timer = max(0, self.__outer._movement_timer - 1)
            self._status = bt.Status.SUCCESS

    class IncreaseHunger(bt.Action):
        """Increases the rabbit's hunger."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._hunger += self.__outer._hunger_speed
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

            # Tiredness

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

            if hunger < HUNGER_SEEK_THRESHOLD and thirst < THIRST_SEEK_THRESHOLD and tired < TIRED_SEEK_THRESHOLD:
                self.__outer._health += HEAL_AMOUNT

    class CanMove(bt.Condition):
        """Check if the rabbit can move."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._movement_timer == 0

    ##########
    # HUNGER #
    ##########

    class Hungry(bt.Condition):
        """Check if the rabbit is hungry."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._hunger >= HUNGER_SEEK_THRESHOLD

    class FoodAdjacent(bt.Condition):
        """Check if there is food next to the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            if ecosystem.plant_map[x][y] and ecosystem.plant_map[x][y].type == organisms.Type.GRASS:
                return True

            if ecosystem.flower_map[x][y]:
                return True

            return False

    class Eat(bt.Action):
        """Eats the food on the cell."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            # Prioritize flowers
            if ecosystem.flower_map[x][y]:
                ecosystem.flower_map[x][y] = None
                self.__outer._hunger = max(0, self.__outer._hunger - FLOWER_HUNGER_SATISFACTION)
                # TODO: Make poop contain flower seeds
                # TODO: Make hunger being negative result in size increase
            elif ecosystem.plant_map[x][y]:
                ecosystem.plant_map[x][y].amount -= GRASS_EATING_AMOUNT
                self.__outer._hunger = max(0, self.__outer._hunger - GRASS_HUNGER_SATISFACTION)

    ###################
    # RANDOM MOVEMENT #
    ###################

    class MoveRandomly(bt.Action):
        """Moves the rabbit randomly."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            # TODO: Make excessive movement result in size decrease
            x = self.__outer.x
            y = self.__outer.y
            direction = random.choice(list(helpers.Direction))
            dx = direction.value[0]
            dy = direction.value[1]

            if x + dx < 0 or x + dx >= self.__outer._ecosystem.width or y + dy < 0 or y + dy >= self.__outer._ecosystem.height:
                self._status = bt.Status.FAIL
            elif self.__outer._ecosystem.water_map[x + dx][y + dy]:
                self._status = bt.Status.FAIL
            elif self.__outer._ecosystem.animal_map[x + dx][y + dy]:
                occupied_space = 0
                if self.__outer._ecosystem.plant_map[x + dx][y + dy] and self.__outer._ecosystem.plant_map[x + dx][y + dy].type == organisms.Type.TREE:
                    occupied_space += 50
                for animal in self.__outer._ecosystem.animal_map[x + dx][y + dy]:
                    occupied_space += animal.size
                from ecosystem import ANIMAL_CELL_CAPACITY
                if occupied_space + self.__outer.size > ANIMAL_CELL_CAPACITY:
                    self._status = bt.status.FAIL
            else:
                self._status = bt.Status.SUCCESS
                self.__outer._movement_timer += self.__outer._movement_cooldown
                self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
                self.__outer.x += dx
                self.__outer.y += dy
                self.__outer._ecosystem.animal_map[x + dx][y + dy].append(self.__outer)
