import organisms
import behaviour_tree as bt

LIFE_LENGTH = 24 * 7

class Burrow(organisms.Organism):
    """Defines the burrow, which is just an immovable object."""
    def __init__(self, ecosystem, x, y, size=-100):
        super().__init__(ecosystem, organisms.Type.BURROW, x, y)
        self.size = size

        self._time_since_used = 0

    def get_image(self):
        return 'images/rabbitBurrow.png'

    def generate_tree(self):
        """Generates the tree for the burrow."""
        tree = bt.Sequence()

        tree.add_child(self.IncreaseTimeSinceUsed(self))


        return tree

    class IncreaseTimeSinceUsed(bt.Action):
        """Keeps track of the time since last used."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            ecosystem = self.__outer._ecosystem
            x = self.__outer.x
            y = self.__outer.y

            if len(ecosystem.animal_map[x][y]) > 1:
                for animal in ecosystem.animal_map[x][y]:
                    if animal.type == organisms.Type.RABBIT:
                        self.__outer._time_since_used = 0
                        self._status = bt.Status.SUCCESS
                        break
            else:
                self.__outer._time_since_used += 1

                if self.__outer._time_since_used >= LIFE_LENGTH:
                    for i in range(ecosystem.width):
                        for j in range(ecosystem.height):
                            for animal in ecosystem.animal_map[i][j]:
                                if animal.type == organisms.Type.RABBIT:
                                    if animal.burrow == self.__outer:
                                        animal.burrow = None
                    ecosystem.animal_map[x][y].remove(self.__outer)
                    self._status = bt.Status.FAIL
                else:
                    self._status = bt.Status.SUCCESS
