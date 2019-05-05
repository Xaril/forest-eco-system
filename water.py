import organisms
import behaviour_tree as bt

class Water(organisms.Organism):
    """Defines the small water pool, which is just an immovable object"""
    def __init__(self, ecosystem, x, y):
        super().__init__(ecosystem, organisms.Type.WATER, x, y)

    def get_image(self):
        return 'images/water.png'

    def generate_tree(self):
        """Generates the tree for the water."""
        tree = bt.FallBack()
        return tree
