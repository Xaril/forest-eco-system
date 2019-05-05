import organisms
from earth import Earth
import behaviour_tree as bt

REPRODUCTION_THRESHOLD = 60
GROWTH_SPEED = 0.3 # Based on that grass takes two weeks to grow

class Grass(organisms.Organism):
    """Defines the grass."""
    def __init__(self, ecosystem, x, y, amount):
        super().__init__(ecosystem, organisms.Type.GRASS, x, y)
        self._amount = amount

    def get_image(self):
        if self._amount < REPRODUCTION_THRESHOLD:
            return 'images/grassLow.png'
        else:
            return 'images/grassHigh.png'


    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.Sequence()
        dead_or_alive = bt.FallBack()
        dead_or_alive.add_child(self.IsAlive(self))
        dead_or_alive.add_child(self.Die(self))

        tree.add_child(dead_or_alive)
        tree.add_child(self.Grow(self))
        return tree

    class IsAlive(bt.Condition):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._amount > 0

    class Die(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            earth = Earth(self.__outer._ecosystem, x, y)
            self.__outer._ecosystem.plant_map[x][y] = earth
            self.__outer._ecosystem.organisms.append(earth)
            self.__outer.dead = True
            self._status = bt.Status.FAIL


    class Grow(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._amount = min(100, self.__outer._amount + GROWTH_SPEED)
            self._status = bt.Status.SUCCESS
