import organisms
import behaviour_tree as bt

class Hive(organisms.Organism):
    """Defines the hive, which is just an immovable object."""
    def __init__(self, ecosystem, x, y, size=10):
        super().__init__(ecosystem, organisms.Type.HIVE, x, y)
        self.size = size

    def get_image(self):
        return 'images/hive.png'

    def generate_tree(self):
        """Generates the tree for the hive."""
        tree = bt.FallBack()
        return tree
