import organisms
import behaviour_tree as bt

class Burrow(organisms.Organism):
    """Defines the burrow, which is just an immovable object."""
    def __init__(self, ecosystem, x, y, size=-100):
        super().__init__(ecosystem, organisms.Type.BURROW, x, y)
        self.size = size

    def get_image(self):
        return 'images/rabbitBurrow.png'

    def generate_tree(self):
        """Generates the tree for the burrow."""
        tree = bt.FallBack()
        return tree
