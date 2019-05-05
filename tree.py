import organisms
import behaviour_tree as bt

class Tree(organisms.Organism):
    """Defines the tree, which is just an immovable object."""
    def __init__(self, ecosystem, x, y):
        super().__init__(ecosystem, organisms.Type.TREE, 'images/tree.png', x, y)

    def generate_tree(self):
        """Generates the tree for the tree."""
        tree = bt.FallBack()
        return tree
