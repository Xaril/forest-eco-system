import random
from tree import Tree
from grass import Grass
from earth import Earth
from flower import Flower

TREE_PERCENTAGE = 0.1
GRASS_INIT_PERCENTAGE = 0.2
FLOWER_PERCENTAGE = 0.03

class Ecosystem():
    """Defines an ecosystem, which starts out as a map of a forest/field with
    initial populations."""
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Initialize ecosystem maps
        self.plant_map = []
        for x in range(self.width):
            self.plant_map.append([])
            for y in range(self.height):
                self.plant_map[x].append(None)

        self.flower_map = []
        for x in range(self.width):
            self.flower_map.append([])
            for y in range(self.height):
                self.flower_map[x].append(None)

        # Add initial organisms
        self.initialize_forest()

    def initialize_forest(self):
        """Adds initial organisms to the map."""
        # Plant map
        for x in range(self.width):
            for y in range(self.height):
                if random.random() <= TREE_PERCENTAGE:
                    tree = Tree(self, x, y)
                    self.plant_map[x][y] = tree
                elif random.random() <= GRASS_INIT_PERCENTAGE:
                    grass = Grass(self, x, y, random.randint(1,101))
                    self.plant_map[x][y] = grass
                else:
                    earth = Earth(self, x, y)
                    self.plant_map[x][y] = earth

        # Flower map
        for x in range(self.width):
            for y in range(self.height):
                if random.random() <= FLOWER_PERCENTAGE:
                    flower = Flower(self, x, y, False)
                    self.flower_map[x][y] = flower

    def get_organisms_from_maps(self):
        """Looks through the maps to find organisms, and returns these in a list."""
        organisms = []

        # Plant map
        for x in range(self.width):
            for y in range(self.height):
                if self.plant_map[x][y]:
                    organisms.append(self.plant_map[x][y])

        # Flower map
        for x in range(self.width):
            for y in range(self.height):
                if self.flower_map[x][y]:
                    organisms.append(self.flower_map[x][y])

        # Animal map

        return organisms

    def remove_dead_organisms(self, organisms):
        organisms = [organism for organism in organisms if not organism.dead]

    def run(self):
        """Run the behaviour of all organisms for one time step."""
        organisms = self.get_organisms_from_maps()

        for organism in organisms:
            organism.run()

        self.remove_dead_organisms(organisms)

        return organisms
