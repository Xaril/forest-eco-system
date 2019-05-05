import organisms
import behaviour_tree as bt


class Flower(organisms.Organism):
    """Defines the flower."""
    def __init__(self, ecosystem, x, y, seed):
        super().__init__(ecosystem, organisms.Type.FLOWER, x, y)
        self._seed = seed

    def get_image(self):
        if self._seed:
            return 'images/flowerSeed.png'
        else:
            return 'images/flower.png'


    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.Sequence()
        return tree
