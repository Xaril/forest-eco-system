import organisms
import behaviour_tree as bt

class Earth(organisms.Organism):
    """Defines the earth."""
    def __init__(self, ecosystem, x, y):
        super().__init__(ecosystem, organisms.Type.EARTH, x, y)

    def get_image(self):
        return 'images/earth.png'

    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.FallBack()
        return tree
