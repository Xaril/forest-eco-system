import organisms
import behaviour_tree as bt
import helpers
import random

HUNGER_SEEK_THRESHOLD = 50
THIRST_SEEK_THRESHOLD = 50
TIRED_SEEK_THRESHOLD = 50
HUNGER_DAMAGE_THRESHOLD = 75
THIRST_DAMAGE_THRESHOLD = 85
TIRED_DAMAGE_THRESHOLD = 80

REPRODUCTION_TIME = 24*30 # Rabbits are pregnant for 30 days
REPRODUCTION_COOLDOWN = 24*5 # Rabbits usually have to wait 5 days before being able to reproduce again


class Rabbit(organisms.Organism):
    """Defines the rabbit."""
    def __init__(self, ecosystem, x, y, female, adult=False, hunger=50,
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

        logic_fallback = bt.FallBack()
        tree.add_child(logic_fallback)
        # Sleeping

        # Dying

        # Avoiding enemies

        # Eating

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

    class ReduceMovementTimer(bt.Action):
        """Ticks down the movement timer for the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._movement_timer = max(0, self.__outer._movement_timer - 1)
            self._status = bt.Status.SUCCESS

    class CanMove(bt.Condition):
        """Check if rabbit can move."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._movement_timer == 0

    class MoveRandomly(bt.Action):
        """Moves the rabbit randomly."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
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
