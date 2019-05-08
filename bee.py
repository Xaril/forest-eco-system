import organisms
import behaviour_tree as bt

class Bee(organisms.Organism):
    """Defines the bee."""
    def __init__(self, ecosystem, x, y):
        super().__init__(ecosystem, organisms.Type.BEE, x, y)
        self.size = 0
    def get_image(self):
        return 'images/Bee.png'

    def generate_tree(self):
        """Generates the tree for the bee."""
        tree = bt.FallBack()
        return tree
