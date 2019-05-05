import random
from tree import Tree
from grass import Grass
from earth import Earth

TREE_PERCENTAGE = 0.1
GRASS_INIT_PERCENTAGE = 0.2

class Ecosystem():
    """Defines an ecosystem, which starts out as a map of a forest/field with
    initial populations."""
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Initialize ecosystem map
        self.map = []
        for x in range(self.width):
            self.map.append([])
            for y in range(self.height):
                self.map[x].append(None)

        self.organisms = []

        # Add immovable trees to the map
        self.add_trees()

    def add_trees(self):
        """Adds trees to the map."""
        for x in range(self.width):
            for y in range(self.height):
                if random.random() <= TREE_PERCENTAGE:
                    tree = Tree(self, x, y)
                    self.organisms.append(tree)
                    self.map[x][y] = tree
                elif random.random() <= GRASS_INIT_PERCENTAGE:
                    grass = Grass(self, x, y, random.randint(1,101))
                    self.organisms.append(grass)
                    self.map[x][y] = grass
                else:
                    earth = Earth(self, x, y)
                    self.organisms.append(earth)
                    self.map[x][y] = earth

    def run(self):
        """Run the behaviour of all organisms for one time step."""
        for organism in self.organisms:
            organism.run()

        return self.organisms
