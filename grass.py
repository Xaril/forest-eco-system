import organisms
import random
from earth import Earth
import behaviour_tree as bt

REPRODUCTION_THRESHOLD = 60
GROWTH_SPEED = 0.3 # Based on that grass takes two weeks to grow
PLANTED_SEED_AMOUNT = -80 # With growth speed of 0.3 this will make SEED-GRASS transition take approx 10 days
REPRODUCTION_COOLDOWN = 24 # Reproduces only once a day

class Grass(organisms.Organism):
    """Defines the grass."""
    def __init__(self, ecosystem, x, y, amount, seed_planted):
        super().__init__(ecosystem, organisms.Type.GRASS, x, y)
        self._amount = amount
        self._seed_planted = seed_planted
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

        reproduce_sequence = bt.Sequence()
        reproduce_sequence.add_child(self.CanReproduce(self))
        reproduce_sequence.add_child(self.Reproduce(self))

        tree.add_child(dead_or_alive_fallback)
        tree.add_child(self.Grow(self))
        tree.add_child(reproduce_sequence)
        return tree

    class IsAlive(bt.Condition):
        """Check if grass is alive."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._amount > 0 or self.__outer._seed_planted

    class Die(bt.Action):
        """Performs action after grass dies."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            earth = Earth(self.__outer._ecosystem, x, y)
            self.__outer._ecosystem.plant_map[x][y] = earth
            self.__outer.dead = True
            self._status = bt.Status.FAIL


    class Grow(bt.Action):
        """Makes the tree grow."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._amount = min(100, self.__outer._amount + GROWTH_SPEED)
            if self.__outer._amount > 0:
                self.__outer._seed_planted = False
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
            self._status = bt.Status.SUCCESS
            # get a random direction
            rand_x_dir  = random.randint(-2,2)
            rand_y_dir = random.randint(-2,2)

            x = self.__outer.x + rand_x_dir
            y = self.__outer.y + rand_y_dir

            # check if in bounds
            if x < 0 or x >= self.__outer._ecosystem.width or y < 0 or y >= self.__outer._ecosystem.height:
                return
            # if cell is empty or earth plant a seed
            if self.__outer._ecosystem.plant_map[x][y] and self.__outer._ecosystem.plant_map[x][y].type == organisms.Type.EARTH:
                grass = Grass(self.__outer._ecosystem, x, y, PLANTED_SEED_AMOUNT, True)
                self.__outer._ecosystem.plant_map[x][y] = grass
                self.__outer._hours_since_last_reproduction = 0
