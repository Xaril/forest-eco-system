import organisms
import behaviour_tree as bt

REPRODUCTION_THRESHOLD = 60

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
        tree = bt.FallBack()
        return tree
