import random
from tree import Tree
from grass import Grass
from earth import Earth
from flower import Flower
from rabbit import Rabbit
from burrow import Burrow
from bee import Bee
from hive import Hive
from fox import Fox
from den import Den
from water import Water
from weather import Weather
from helpers import Direction, EuclidianDistance, InverseLerp
import constants
import organisms


TREE_PERCENTAGE = 0.1
GRASS_INIT_PERCENTAGE = 0.2
FLOWER_PERCENTAGE = 0.02
INITAL_WATER_MAX_AMOUNT = 500
WATER_POOLS = [20, 10, 5, 3, 2]
WATER_POOLS_POSITIONS = []
ANIMAL_CELL_CAPACITY = 100
BURROW_PERCENTAGE = 0.002
BURROW_RABBIT_MIN_AMOUNT = 2
BURROW_RABBIT_MAX_AMOUNT = 3
HIVES_PER_TREE = 0.04
HIVE_BEE_MIN_AMOUNT = 5
HIVE_BEE_MAX_AMOUNT = 9
FOX_PERCENTAGE = 0.0025


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
                self.flower_map[x].append([])

        self.animal_map = []
        for x in range(self.width):
            self.animal_map.append([])
            for y in range(self.height):
                self.animal_map[x].append([])

        self.nectar_smell_map = []
        for x in range(self.width):
            self.nectar_smell_map.append([])
            for y in range(self.height):
                self.nectar_smell_map[x].append(0)

        self.rabbit_smell_map = []
        for x in range(self.width):
            self.rabbit_smell_map.append([])
            for y in range(self.height):
                self.rabbit_smell_map[x].append(0)

        self.weather = Weather(self)

        # Add initial organisms
        self.initialize_forest()

    def initialize_forest(self):
        """Adds initial organisms to the map."""

        directions = list(Direction)
        # Water map
        for pool_size in WATER_POOLS:
            rand_x = random.randint(0, self.width - 1)
            rand_y = random.randint(0, self.height - 1)
            while self.water_map[rand_x][rand_y]:
                rand_x = random.randint(0, self.width - 1)
                rand_y = random.randint(0, self.height - 1)
            water_pools_added = 0
            positions = [(rand_x,rand_y)]
            WATER_POOLS_POSITIONS.append((rand_x,rand_y))
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
                    if random.random() <= HIVES_PER_TREE:
                        hive = Hive(self, x, y)
                        self.animal_map[x][y].append(hive)
                        bee_amount = random.randint(HIVE_BEE_MIN_AMOUNT, HIVE_BEE_MAX_AMOUNT)
                        bee = Bee(self, x, y, hive=hive, scout=True, age=random.randint(0,24*150))
                        hive.bees.append(bee)
                        self.animal_map[x][y].append(bee)
                        for _ in range(bee_amount):
                            bee = Bee(self, x, y, hive=hive, scout=False,age=random.randint(0,24*150))
                            self.animal_map[x][y].append(bee)
                            hive.bees.append(bee)
                elif random.random() <= GRASS_INIT_PERCENTAGE:
                    grass = Grass(self, x, y, random.randint(-80, 100), None, self.get_initial_water_level(x,y))
                    self.plant_map[x][y] = grass
                else:
                    earth = Earth(self, x, y, self.get_initial_water_level(x,y))
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
                    flower = Flower(self, x, y, random.randint(-50, 100), nectar=random.randint(0,100))
                    self.flower_map[x][y].append(flower)

        # Animal map
        for x in range(self.width):
            for y in range(self.height):
                if self.water_map[x][y]:
                    continue
                # Rabbits
                if random.random() <= BURROW_PERCENTAGE:
                    burrow = Burrow(self, x, y)
                    self.animal_map[x][y].append(burrow)
                    rabbit_amount = random.randint(BURROW_RABBIT_MIN_AMOUNT, BURROW_RABBIT_MAX_AMOUNT)
                    for _ in range(rabbit_amount):
                        dx = random.randint(-3, 3)
                        dy = random.randint(-3, 3)

                        if x + dx < 0 or x + dx >= self.width or y + dy < 0 or y + dy >= self.height:
                            continue

                        if self.water_map[x + dx][y + dy]:
                            continue

                        rabbit = Rabbit(self, x + dx, y + dy,
                                        random.choice([True, False]),
                                        adult=True, burrow=burrow,
                                        age=random.randint(24*365, 24*365*2))
                        self.animal_map[x + dx][y + dy].append(rabbit)

                # Foxes
                if random.random() <= FOX_PERCENTAGE:
                    fox = Fox(self, x, y,
                              random.choice([True, False]),
                              adult=True, age=random.randint(24*365, 24*365*4))
                    self.animal_map[x][y].append(fox)



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
                for flower in self.flower_map[x][y]:
                    organisms.append(flower)

        # Animal map
        for x in range(self.width):
            for y in range(self.height):
                for animal in self.animal_map[x][y]:
                    organisms.append(animal)

        return organisms


    def get_initial_water_level(self, x, y):
        """Calulate initial water level on earth and grass depending on the proximity to water supplies"""
        max_possible_distance = EuclidianDistance(0, 0, self.width - 1, self.height - 1)
        closest_lake_distance = EuclidianDistance(x, y, WATER_POOLS_POSITIONS[0][0], WATER_POOLS_POSITIONS[0][1])
        min_distance_lake_index = 0
        for (index, lake_position) in enumerate(WATER_POOLS_POSITIONS):
            distace = EuclidianDistance(x, y , lake_position[0], lake_position[1])
            if distace < closest_lake_distance:
                closest_lake_distance = distace
                min_distance_lake_index = index

        return INITAL_WATER_MAX_AMOUNT * (1 - InverseLerp(0, max_possible_distance, closest_lake_distance))

    def reset_nectar_smell_map(self):
        for x in range(self.width):
            for y in range(self.height):
                self.nectar_smell_map[x][y] = 0

    def update_rabbit_smell_map(self):
        for x in range(self.width):
            for y in range(self.height):
                found_rabbit = False
                for animal in self.animal_map[x][y]:
                    if animal.type == organisms.Type.RABBIT:
                        found_rabbit = True
                        break

            if found_rabbit:
                self.rabbit_smell_map[x][y] = 1
            else:
                self.rabbit_smell_map[x][y] *= 2/3

    def run(self):
        """Run the behaviour of all organisms for one time step."""
        organisms = self.get_organisms_from_maps()

        self.weather.simulate_weather()

        self.update_rabbit_smell_map()

        for organism in organisms:
            organism.run()

        organisms = self.get_organisms_from_maps()
        self.reset_nectar_smell_map()

        return organisms
