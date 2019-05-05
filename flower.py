import organisms
import behaviour_tree as bt


REPRODUCTION_THRESHOLD = 60 # Amout of flower needed to be able to reproduce
GROWTH_SPEED = 0.1 # Based on that grass takes around five weeks to grow
PLANTED_SEED_AMOUNT = -50 # With growth speed of 0.1 this will make SEED-GRASS transition take approx 3 weeks
MAX_FLOWER_AMOUNT = 100

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
            return self.__outer._amount > 0 or self.__outer._seed

    class Die(bt.Action):
        """Performs action after grass dies."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer.dead = True
            self._status = bt.Status.FAIL


    class Grow(bt.Action):
        """Makes the tree grow."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._amount = min(MAX_FLOWER_AMOUNT, self.__outer._amount + GROWTH_SPEED)
            if self.__outer._amount > 0:
                self.__outer._seed = False
            self._status = bt.Status.SUCCESS
