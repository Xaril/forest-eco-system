import organisms
from bee import Bee
import behaviour_tree as bt

HIVE_FOOD_CONSUMPTION = 0.1
HIVE_BEE_MAKING_THRESHOLD = 101
BEE_FOOD_COST = 20

class Hive(organisms.Organism):
    """Defines the hive, which is just an immovable object."""
    def __init__(self, ecosystem, x, y, size=10, food=100):
        super().__init__(ecosystem, organisms.Type.HIVE, x, y)
        self.size = size
        self.food = food

    def get_image(self):
        return 'images/hive.png'

    def generate_tree(self):
        """Generates the tree for the hive."""
        tree = bt.FallBack()

        is_dead_sequence = bt.Sequence()
        is_dead_sequence.add_child(self.Dying(self))
        is_dead_sequence.add_child(self.Die(self))

        sequence = bt.Sequence()
        sequence.add_child(self.DecreaseFood(self))
        create_bee_sequence = bt.Sequence()
        create_bee_sequence.add_child(self.CanCreateBee(self))
        create_bee_sequence.add_child(self.CreateBee(self))
        sequence.add_child(create_bee_sequence)

        tree.add_child(is_dead_sequence)
        tree.add_child(sequence)
        return tree


    class DecreaseFood(bt.Action):
        """Decreses the amount of available food."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._food = max(0, self.__outer.food - HIVE_FOOD_CONSUMPTION)
            self._status = bt.Status.SUCCESS

    class Dying(bt.Condition):
        """Check if the hive is dying."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.food <= 0

    class Die(bt.Action):
        """Destroy the hive."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
            for animals in self.__outer._ecosystem.animal_map[x][y]:
                if animal.type == organism.Type.Bee:
                    animal.in_hive = False
                    animal.hive = None
            self._status = bt.Status.SUCCESS



    class CanCreateBee(bt.Condition):
        """Check if the hive can create a bee"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._food >= HIVE_BEE_MAKING_THRESHOLD


    class CreateBee(bt.Action):
            def __init__(self, outer):
                super().__init__()
                self.__outer = outer

            def action(self):
                x = self.__outer.x
                y = self.__outer.y
                bee = Bee(self.__outer._ecosystem,x, y, hive = self.__outer)
                self.__outer._ecosystem.animal_map[x][y].append(bee)
                self._status = bt.Status.SUCCESS
