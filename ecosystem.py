import random
from enum import Enum
from tree import Tree
from grass import Grass
from earth import Earth
from flower import Flower
from water import Water

TREE_PERCENTAGE = 0.1
GRASS_INIT_PERCENTAGE = 0
FLOWER_PERCENTAGE = 0.03
WATER_POOLS = [20, 10, 5, 5, 5, 3, 1]


class Direction(Enum):
    """The different directions."""
    CENTER = (0, 0)
    EAST = (1, 0)
    NORTH = (0, 1)
    NORTHEAST = (1, 1)
    NORTHWEST = (-1, 1)
    SOUTH = (0, -1)
    SOUTHEAST = (1, -1)
    SOUTHWEST = (-1, -1)
    WEST = (-1, 0)

class Ecosystem():
    """Defines an ecosystem, which starts out as a map of a forest/field with
    initial populations."""
    def __init__(self, width, height):
        self.width = width
        self.height = height


        self.water_map = []
        for x in range(self.width):
            self.water_map.append([])
            for y in range(self.height):
                self.water_map[x].append(None)

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

        directions = list(Direction)
        # Water map
        for pool_size in WATER_POOLS:
            rand_x = random.randint(0, self.width - 1)
            rand_y = random.randint(0, self.height - 1)
            water_pools_added = 0
            positions = [(rand_x,rand_y)]
            while water_pools_added < pool_size and positions:
                # Breadth first add water pools around
                x, y = positions.pop(0)
                if not self.water_map[x][y]:
                    water = Water(self, x, y)
                    self.water_map[x][y] = water
                    water_pools_added += 1
                    # Insert all neighbors
                    random.shuffle(directions) # shuffle for a bit random shapes
                    for dir in directions:
                        new_x = x + dir.value[0]
                        new_y = y + dir.value[1]
                        # Check if out of bounds
                        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                            continue
                        if self.water_map[new_x][new_y]:
                            continue
                        positions.append((new_x,new_y))



        # Plant map
        for x in range(self.width):
            for y in range(self.height):
                # check if water
                if self.water_map[x][y]:
                    continue
                if random.random() <= TREE_PERCENTAGE:
                    tree = Tree(self, x, y)
                    self.plant_map[x][y] = tree
                elif random.random() <= GRASS_INIT_PERCENTAGE:
                    grass = Grass(self, x, y, random.randint(-80, 101))
                    self.plant_map[x][y] = grass
                else:
                    earth = Earth(self, x, y)
                    self.plant_map[x][y] = earth

        # Flower map
        from organisms import Type
        for x in range(self.width):
            for y in range(self.height):
                if self.water_map[x][y]:
                    continue
                if random.random() <= FLOWER_PERCENTAGE:
                    if self.plant_map[x][y] and self.plant_map[x][y].type == Type.TREE:
                        continue
                    flower = Flower(self, x, y, random.randint(-50, 101))
                    self.flower_map[x][y] = flower

    def get_organisms_from_maps(self):
        """Looks through the maps to find organisms, and returns these in a list."""
        organisms = []

        # Water map
        for x in range(self.width):
            for y in range(self.height):
                if self.water_map[x][y]:
                    organisms.append(self.water_map[x][y])

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


    def run(self):
        """Run the behaviour of all organisms for one time step."""
        organisms = self.get_organisms_from_maps()

        for organism in organisms:
            organism.run()

        return organisms
