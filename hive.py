import organisms
from bee import Bee
import behaviour_tree as bt

HIVE_FOOD_CONSUMPTION = 0.1
HIVE_BEE_MAKING_THRESHOLD = 100
BEE_FOOD_COST = 5

class Hive(organisms.Organism):
    """Defines the hive, which is just an immovable object."""
    def __init__(self, ecosystem, x, y, size=10, food=300, capacity=10):
        super().__init__(ecosystem, organisms.Type.HIVE, x, y)
        self.size = size
        self.food = food
        self.bees = []
        self._capacity = capacity
        self.has_scout = True

    def get_image(self):
        return 'images/hive.png'

    def generate_tree(self):
        """Generates the tree for the hive."""
        tree = bt.FallBack()

        sequence = bt.Sequence()
        create_bee_sequence = bt.Sequence()
        create_bee_sequence.add_child(self.ShouldCreateBee(self))
        create_bee_sequence.add_child(self.HaveEnoughtRoom(self))
        create_bee_sequence.add_child(self.CreateBee(self))
        sequence.add_child(create_bee_sequence)

        tree.add_child(sequence)
        return tree



    class ShouldCreateBee(bt.Condition):
        """Check if the hive can create a bee"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.food >= HIVE_BEE_MAKING_THRESHOLD or (self.__outer.food >= BEE_FOOD_COST and len(self.__outer.bees) <= 5 )


    class HaveEnoughtRoom(bt.Condition):
        """Check if there is enough room in the hive"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._capacity > len(self.__outer.bees)


    class CreateBee(bt.Action):
            def __init__(self, outer):
                super().__init__()
                self.__outer = outer

            def action(self):
                x = self.__outer.x
                y = self.__outer.y
                bee = Bee(self.__outer._ecosystem,x, y, hive = self.__outer)
                self.__outer._ecosystem.animal_map[x][y].append(bee)
                self.__outer.bees.append(bee)
                self.__outer.food -= BEE_FOOD_COST
                self._status = bt.Status.SUCCESS
