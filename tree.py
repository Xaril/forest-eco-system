import organisms
import behaviour_tree as bt

class Tree(organisms.Organism):
    """Defines the tree, which is just an immovable object."""
    def __init__(self, ecosystem, x, y):
        super().__init__(ecosystem, organisms.Type.TREE, x, y)

    def get_image(self):
        return 'images/tree.png'

    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.FallBack()
        return tree
