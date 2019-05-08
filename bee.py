import organisms
import random
import helpers
import behaviour_tree as bt

class Bee(organisms.Organism):
    """Defines the bee."""
    def __init__(self, ecosystem, x, y, hunger=0, tired=0, health=100, life_span=24*150,
                hunger_speed=50/36, tired_speed=50/36,
                vision_range={'left': 4, 'right': 4, 'up': 4, 'down': 4},
                hive=None, in_hive=False, movement_cooldown=4, age=0):
        super().__init__(ecosystem, organisms.Type.BEE, x, y)
        self.size = 0

        self._hunger = hunger
        self._tired = tired
        self._health = health
        self._life_span = life_span
        self._hunger_speed = hunger_speed
        self._tired_speed = tired_speed
        self._vision_range = vision_range
        self._hive = hive
        self._in_hive = in_hive
        self._movement_cooldown = movement_cooldown
        self._age = age

        self._movement_timer = self._movement_cooldown
        self._movement_path = None

    def get_image(self):
        return 'images/Bee.png'

    def generate_tree(self):
        """Generates the tree for the bee."""
        tree = bt.FallBack()

        is_dead_sequence = bt.Sequence()
        is_dead_sequence.add_child(self.Dying(self))
        is_dead_sequence.add_child(self.Die(self))

        sequence = bt.Sequence()
        logic_fallback = bt.FallBack()

        moving_randomly_sequence = bt.Sequence()
        moving_randomly_sequence.add_child(self.CanMove(self))
        moving_randomly_sequence.add_child(self.MoveRandomly(self))
        logic_fallback.add_child(moving_randomly_sequence)

        sequence.add_child(self.ReduceMovementTimer(self))
        sequence.add_child(logic_fallback)

        tree.add_child(is_dead_sequence)
        tree.add_child(sequence)
        return tree


    class Dying(bt.Condition):
        """Check if the bee is dying."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._health <= 0 or self.__outer._age >= self.__outer._life_span

    class Die(bt.Action):
        """Kill the bee."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
            self._status = bt.Status.SUCCESS



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




    class CanMove(bt.Condition):
        """Check if the rabbit can move."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._movement_timer == 0



    ###################
    # RANDOM MOVEMENT #
    ###################

    class MoveRandomly(bt.Action):
        """Moves the bee randomly."""
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
            else:
                self._status = bt.Status.SUCCESS
                self.__outer._movement_timer += self.__outer._movement_cooldown
                self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
                self.__outer.x += dx
                self.__outer.y += dy
                self.__outer._ecosystem.animal_map[x + dx][y + dy].append(self.__outer)
