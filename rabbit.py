import organisms
import behaviour_tree as bt
import helpers
import random
import math
from astar import astar
from grass import MAX_GRASS_AMOUNT
from grass import REPRODUCTION_THRESHOLD as MUCH_GRASS
from water import WATER_POOL_CAPACITY

HUNGER_SEEK_THRESHOLD = 50
THIRST_SEEK_THRESHOLD = 50
TIRED_SEEK_THRESHOLD = 50
HUNGER_DAMAGE_THRESHOLD = 75
THIRST_DAMAGE_THRESHOLD = 85
TIRED_DAMAGE_THRESHOLD = 80
HUNGER_DAMAGE_FACTOR = 0.2
THIRST_DAMAGE_FACTOR = 0.3
TIRED_DAMAGE_FACTOR = 0.1
FLOWER_HUNGER_SATISFACTION = 45
GRASS_HUNGER_SATISFACTION = 20
GRASS_EATING_AMOUNT = 0.2 * MAX_GRASS_AMOUNT
WATER_DRINKING_AMOUNT = 0.001 * WATER_POOL_CAPACITY

EATING_AND_DRINKING_SLEEP_FACTOR = 0.3
SLEEP_TIME = 8

HEAL_AMOUNT = 4

REPRODUCTION_TIME = 24*30 # Rabbits are pregnant for 30 days
REPRODUCTION_COOLDOWN = 24*5 # Rabbits usually have to wait 5 days before being able to reproduce again


class Rabbit(organisms.Organism):
    """Defines the rabbit."""
    def __init__(self, ecosystem, x, y, female, adult=False, hunger=0,
                 thirst=0, tired=0, health=100, size=20, life_span=24*365*5,
                 hunger_speed=50/36, thirst_speed=50/72, tired_speed=50/36,
                 vision_range={'left': 4, 'right': 4, 'up': 4, 'down': 4},
                 burrow=None, in_burrow=False, movement_cooldown=3, age=24*365):
        super().__init__(ecosystem, organisms.Type.RABBIT, x, y)
        self._female = female
        self._adult = adult

        self._hunger = hunger
        self._thirst = thirst
        self._tired = tired
        self._health = health
        self.size = size
        self._life_span = life_span
        self._age = age
        self._hunger_speed = hunger_speed
        self._thirst_speed = thirst_speed
        self._tired_speed = tired_speed
        self._vision_range = vision_range

        # TODO:
        #     * Genetic variables
        #     * Pooping

        self._can_reproduce = self._adult
        self._pregnant = False
        self._partner = None

        self._burrow = burrow
        self._in_burrow = False

        self._asleep = False
        self._sleep_time = 0

        self._movement_cooldown = movement_cooldown
        self._movement_timer = 3
        self._movement_path = None


    def get_image(self):
        if self._adult:
            return 'images/rabbitAdult.png'
        else:
            return 'images/rabbitYoung.png'


    def generate_tree(self):
        """Generates the tree for the rabbit."""
        tree = bt.Sequence()
        tree.add_child(self.ReduceMovementTimer(self))
        tree.add_child(self.IncreaseHunger(self))
        tree.add_child(self.IncreaseThirst(self))
        tree.add_child(self.ChangeTired(self))
        tree.add_child(self.TakeDamage(self))
        tree.add_child(self.ReplenishHealth(self))

        logic_fallback = bt.FallBack()
        tree.add_child(logic_fallback)
        # Sleeping
        sleep_sequence = bt.Sequence()
        logic_fallback.add_child(sleep_sequence)
        sleep_sequence.add_child(self.Sleeping(self))

        sleep_fallback = bt.FallBack()
        sleep_sequence.add_child(sleep_fallback)
        sleep_fallback.add_child(self.ShouldNotWakeUp(self))
        sleep_fallback.add_child(self.WakeUp(self))

        # Dying
        die_sequence = bt.Sequence()
        logic_fallback.add_child(die_sequence)
        die_sequence.add_child(self.Dying(self))
        die_sequence.add_child(self.Die(self))

        # Avoiding enemies

        # Eating
        hungry_sequence = bt.Sequence()
        logic_fallback.add_child(hungry_sequence)
        hungry_sequence.add_child(self.HungrierThanThirsty(self))
        hungry_sequence.add_child(self.HungrierThanTired(self))
        hungry_sequence.add_child(self.Hungry(self))

        hungry_fallback = bt.FallBack()
        hungry_sequence.add_child(hungry_fallback)

        adjacent_food_sequence = bt.Sequence()
        hungry_fallback.add_child(adjacent_food_sequence)
        adjacent_food_sequence.add_child(self.FoodAdjacent(self))
        adjacent_food_sequence.add_child(self.Eat(self))

        food_nearby_sequence = bt.Sequence()
        hungry_fallback.add_child(food_nearby_sequence)
        food_nearby_sequence.add_child(self.FoodNearby(self))
        food_nearby_sequence.add_child(self.CanMove(self))
        food_nearby_sequence.add_child(self.FindPathToFood(self))
        food_nearby_sequence.add_child(self.MoveOnPath(self))
        #TODO: Move away from burrow in search of food

        # Drinking
        thirsty_sequence = bt.Sequence()
        logic_fallback.add_child(thirsty_sequence)
        thirsty_sequence.add_child(self.ThirstierThanTired(self))
        thirsty_sequence.add_child(self.Thirsty(self))

        thirsty_fallback = bt.FallBack()
        thirsty_sequence.add_child(thirsty_fallback)

        adjacent_water_sequence = bt.Sequence()
        thirsty_fallback.add_child(adjacent_water_sequence)
        adjacent_water_sequence.add_child(self.WaterAdjacent(self))
        adjacent_water_sequence.add_child(self.Drink(self))

        water_nearby_sequence = bt.Sequence()
        thirsty_fallback.add_child(water_nearby_sequence)
        # Might want rabbits to only know about water they've seen,
        # instead of knowing about water globally
        water_nearby_sequence.add_child(self.CanMove(self))
        water_nearby_sequence.add_child(self.FindPathToWater(self))
        water_nearby_sequence.add_child(self.MoveOnPath(self))
        #TODO: Move away from burrow in search of food

        # Tiredness

        # Pooping

        # Giving birth

        # Reproducing

        # Moving randomly
        random_movement_sequence = bt.Sequence()
        logic_fallback.add_child(random_movement_sequence)
        random_movement_sequence.add_child(self.CanMove(self))
        random_movement_sequence.add_child(self.MoveRandomly(self))

        return tree

    #####################
    # VARIABLE CONTROLS #
    #####################

    class ReduceMovementTimer(bt.Action):
        """Ticks down the movement timer for the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._movement_timer = max(0, self.__outer._movement_timer - 1)
            self._status = bt.Status.SUCCESS

    class IncreaseHunger(bt.Action):
        """Increases the rabbit's hunger."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            factor = 1 if not self.__outer._asleep else EATING_AND_DRINKING_SLEEP_FACTOR
            self.__outer._hunger += factor * self.__outer._hunger_speed
            self._status = bt.Status.SUCCESS

    class IncreaseThirst(bt.Action):
        """Increases the rabbit's thirst."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            factor = 1 if not self.__outer._asleep else EATING_AND_DRINKING_SLEEP_FACTOR
            self.__outer._thirst += factor * self.__outer._thirst_speed
            self._status = bt.Status.SUCCESS

    class ChangeTired(bt.Action):
        """Changes the rabbit's tiredness depending on if it is awake."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            if not self.__outer._asleep:
                self.__outer._tired += self.__outer._tired_speed
            else:
                self.__outer._tired = max(0, self.__outer._tired - TIRED_DAMAGE_THRESHOLD / SLEEP_TIME)
                self.__outer._sleep_time += 1
            self._status = bt.Status.SUCCESS

    class TakeDamage(bt.Action):
        """Take damage from various sources."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self._status = bt.Status.SUCCESS

            # Hunger
            hunger = self.__outer._hunger
            if hunger >= HUNGER_DAMAGE_THRESHOLD:
                self.__outer._health -= (hunger - HUNGER_DAMAGE_THRESHOLD) * HUNGER_DAMAGE_FACTOR

            # Thirst
            thirst = self.__outer._thirst
            if thirst >= THIRST_DAMAGE_THRESHOLD:
                self.__outer._thirst -= (thirst - THIRST_DAMAGE_THRESHOLD) * THIRST_DAMAGE_FACTOR

            # Tiredness
            tired = self.__outer._tired
            if tired >= TIRED_DAMAGE_THRESHOLD:
                self.__outer._tired -= (tired - TIRED_DAMAGE_THRESHOLD) * TIRED_DAMAGE_FACTOR

    class ReplenishHealth(bt.Action):
        """Replenish health if in a healthy condition."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self._status = bt.Status.SUCCESS

            hunger = self.__outer._hunger
            thirst = self.__outer._thirst
            tired = self.__outer._tired

            if hunger < HUNGER_SEEK_THRESHOLD and thirst < THIRST_SEEK_THRESHOLD and tired < TIRED_SEEK_THRESHOLD:
                self.__outer._health += HEAL_AMOUNT

    ############
    # SLEEPING #
    ############

    class Sleeping(bt.Condition):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._asleep

    class ShouldNotWakeUp(bt.Condition):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._sleep_time < SLEEP_TIME

    class WakeUp(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._asleep = False
            self.__outer._sleep_time = 0
            self._status = bt.Status.SUCCESS

    #########
    # DYING #
    #########

    class Dying(bt.Condition):
        """Check if the rabbit is dying."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._health <= 0 or self.__outer._age >= self.__outer._life_span

    class Die(bt.Action):
        """Kill the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
            self._status = bt.Status.SUCCESS

    ###########
    # ENEMIES #
    ###########

    class CanMove(bt.Condition):
        """Check if the rabbit can move."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._movement_timer == 0

    ##########
    # HUNGER #
    ##########

    class HungrierThanThirsty(bt.Condition):
        """Check if the rabbit is hungrier than it is thirsty."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._hunger >= self.__outer._thirst

    class HungrierThanTired(bt.Condition):
        """Check if the rabbit is hungrier than it is tired."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._hunger >= self.__outer._tired

    class Hungry(bt.Condition):
        """Check if the rabbit is hungry."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._hunger >= HUNGER_SEEK_THRESHOLD

    class FoodAdjacent(bt.Condition):
        """Check if there is food next to the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            if ecosystem.plant_map[x][y] and ecosystem.plant_map[x][y].type == organisms.Type.GRASS:
                return True

            if ecosystem.flower_map[x][y] and not ecosystem.flower_map[x][y].seed:
                return True

            return False

    class Eat(bt.Action):
        """Eats the food on the cell."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            # Prioritize flowers
            if ecosystem.flower_map[x][y] and not ecosystem.flower_map[x][y].seed:
                ecosystem.flower_map[x][y] = None
                self.__outer._hunger = max(0, self.__outer._hunger - FLOWER_HUNGER_SATISFACTION)
                # TODO: Make poop contain flower seeds
                # TODO: Make hunger being negative result in size increase
            elif ecosystem.plant_map[x][y]:
                ecosystem.plant_map[x][y].amount -= GRASS_EATING_AMOUNT
                self.__outer._hunger = max(0, self.__outer._hunger - GRASS_HUNGER_SATISFACTION)

    class FoodNearby(bt.Condition):
        """Determines if there is food near the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            vision_range = self.__outer._vision_range
            ecosystem = self.__outer._ecosystem

            for dx in range(-vision_range['left'], vision_range['right']+1):
                for dy in range(-vision_range['up'], vision_range['down']+1):
                    if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                        continue

                    if ecosystem.plant_map[x + dx][y + dy] and ecosystem.plant_map[x + dx][y + dy].type == organisms.Type.GRASS:
                        return True

                    if ecosystem.flower_map[x + dx][y + dy] and not ecosystem.flower_map[x + dx][y + dy].seed:
                        return True

            return False

    class FindPathToFood(bt.Action):
        """Finds a path to the best visible food."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            vision_range = self.__outer._vision_range
            ecosystem = self.__outer._ecosystem

            # If the rabbit is very hungry, it should find the closest food
            # instead of the best food.
            find_closest = self.__outer._hunger >= helpers.Lerp(HUNGER_SEEK_THRESHOLD, HUNGER_DAMAGE_THRESHOLD, 2/3)

            best_food = None
            best_distance = math.inf

            if find_closest:
                # Just find the closest food, picking flowers over grass if they are the same distance
                for dx in range(-vision_range['left'], vision_range['right']+1):
                    for dy in range(-vision_range['up'], vision_range['down']+1):
                        if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                            continue

                        distance = helpers.EuclidianDistance(x, y, x + dx, y + dy)
                        if distance < best_distance:
                            if ecosystem.flower_map[x + dx][y + dy] and not ecosystem.flower_map[x + dx][y + dy].seed:
                                best_food = ecosystem.flower_map[x + dx][y + dy]
                                best_distance = distance
                            elif ecosystem.plant_map[x + dx][y + dy] and ecosystem.plant_map[x + dx][y + dy].type == organisms.Type.GRASS:
                                best_food = ecosystem.plant_map[x + dx][y + dy]
                                best_distance = distance
            else:
                # Pick the closest flower if they exist, otherwise pick the closest
                # grass patch with much grass if it exists, otherwise pick the closest grass patch
                for dx in range(-vision_range['left'], vision_range['right']+1):
                    for dy in range(-vision_range['up'], vision_range['down']+1):
                        if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                            continue

                        distance = helpers.EuclidianDistance(x, y, x + dx, y + dy)
                        if best_food:
                            if best_food.type == organisms.Type.FLOWER:
                                if ecosystem.flower_map[x + dx][y + dy] and not ecosystem.flower_map[x + dx][y + dy].seed:
                                    if distance < best_distance:
                                        best_food = ecosystem.flower_map[x + dx][y + dy]
                                        best_distance = distance
                            elif best_food.type == organisms.Type.GRASS:
                                # Found a flower, that is the best food.
                                if ecosystem.flower_map[x + dx][y + dy] and not ecosystem.flower_map[x + dx][y + dy].seed:
                                    best_food = ecosystem.flower_map[x + dx][y + dy]
                                    best_distance = distance
                                else:
                                    # Only consider patches with lots of grass
                                    if best_food.amount >= MUCH_GRASS:
                                        if ecosystem.plant_map[x + dx][y + dy] and ecosystem.plant_map[x + dx][y + dy].type == organisms.Type.GRASS:
                                            if ecosystem.plant_map[x + dx][y + dy].amount >= MUCH_GRASS:
                                                if distance < best_distance:
                                                    best_food = ecosystem.plant_map[x + dx][y + dy]
                                                    best_distance = distance
                                    else:
                                        # Prioritize patches of much grass over those with low amounts
                                        if ecosystem.plant_map[x + dx][y + dy] and ecosystem.plant_map[x + dx][y + dy].type == organisms.Type.GRASS:
                                            if ecosystem.plant_map[x + dx][y + dy].amount >= MUCH_GRASS:
                                                best_food = ecosystem.plant_map[x + dx][y + dy]
                                                best_distance = distance
                                            else:
                                                if distance < best_distance:
                                                    best_food = ecosystem.plant_map[x + dx][y + dy]
                                                    best_distance = distance
                        else:
                            if ecosystem.flower_map[x + dx][y + dy] and not ecosystem.flower_map[x + dx][y + dy].seed:
                                best_food = ecosystem.flower_map[x + dx][y + dy]
                                best_distance = distance
                            elif ecosystem.plant_map[x + dx][y + dy] and ecosystem.plant_map[x + dx][y + dy].type == organisms.Type.GRASS:
                                best_food = ecosystem.plant_map[x + dx][y + dy]
                                best_distance = distance

            path = astar(self.__outer, ecosystem.water_map, ecosystem.plant_map, ecosystem.animal_map,
                               x, y, best_food.x, best_food.y, max_path_length=10)
            if len(path) > 0:
                path.pop(0)
                self.__outer._movement_path = path
                self._status = bt.Status.SUCCESS
            else:
                self.__outer._movement_path = None
                self._status = bt.Status.FAIL


    class MoveOnPath(bt.Action):
        """Moves on the current path."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            path = self.__outer._movement_path

            if not path:
                self._status = bt.Status.FAIL
            else:
                next_point = path.pop(0)
                x = next_point[0]
                y = next_point[1]
                if helpers.EuclidianDistance(self.__outer.x, self.__outer.y, x, y) <= 2:
                    self._status = bt.Status.SUCCESS
                    self.__outer._movement_timer += self.__outer._movement_cooldown
                    self.__outer._ecosystem.animal_map[self.__outer.x][self.__outer.y].remove(self.__outer)
                    self.__outer.x = x
                    self.__outer.y = y
                    self.__outer._ecosystem.animal_map[x][y].append(self.__outer)
                else:
                    self._status = bt.Status.FAIL

    ##########
    # THIRST #
    ##########

    class ThirstierThanTired(bt.Condition):
        """Check if the rabbit is thrstier than it is tired."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._thirst >= self.__outer._tired

    class Thirsty(bt.Condition):
        """Check if the rabbit is thirsty."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._thirst >= THIRST_SEEK_THRESHOLD

    class WaterAdjacent(bt.Condition):
        """Check if there is water next to the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            for direction in list(helpers.Direction):
                dx = direction.value[0]
                dy = direction.value[1]

                if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                    continue

                if ecosystem.water_map[x + dx][y + dy]:
                    return True

            return False

    class Drink(bt.Action):
        """Drinks from an adjacent cell."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            self._status = bt.Status.FAIL
            for direction in list(helpers.Direction):
                dx = direction.value[0]
                dy = direction.value[1]

                if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                    continue

                if ecosystem.water_map[x + dx][y + dy]:
                    ecosystem.water_map[x + dx][y + dy].water_amount -= WATER_DRINKING_AMOUNT
                    self.__outer._thirst = 0
                    self._status = bt.Status.SUCCESS
                    break

    class FindPathToWater(bt.Action):
        """Finds a path to the best water source."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            best_water = None
            best_distance = math.inf

            for water_x in range(ecosystem.width):
                for water_y in range(ecosystem.height):
                    distance = helpers.EuclidianDistance(x, y, water_x, water_y)
                    if distance < best_distance:
                        if ecosystem.water_map[water_x][water_y]:
                            best_water = ecosystem.water_map[water_x][water_y]
                            best_distance = distance


            path = astar(self.__outer, ecosystem.water_map, ecosystem.plant_map, ecosystem.animal_map,
                               x, y, best_water.x, best_water.y, max_path_length=10)
            if len(path) > 0:
                path.pop(0)
                self.__outer._movement_path = path
                self._status = bt.Status.SUCCESS
            else:
                self.__outer._movement_path = None
                self._status = bt.Status.FAIL

    ###################
    # RANDOM MOVEMENT #
    ###################

    class MoveRandomly(bt.Action):
        """Moves the rabbit randomly."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            # TODO: Make excessive movement result in size decrease
            x = self.__outer.x
            y = self.__outer.y
            direction = random.choice(list(helpers.Direction))
            dx = direction.value[0]
            dy = direction.value[1]

            if x + dx < 0 or x + dx >= self.__outer._ecosystem.width or y + dy < 0 or y + dy >= self.__outer._ecosystem.height:
                self._status = bt.Status.FAIL
            elif self.__outer._ecosystem.water_map[x + dx][y + dy]:
                self._status = bt.Status.FAIL
            elif self.__outer._ecosystem.animal_map[x + dx][y + dy]:
                occupied_space = 0
                if self.__outer._ecosystem.plant_map[x + dx][y + dy] and self.__outer._ecosystem.plant_map[x + dx][y + dy].type == organisms.Type.TREE:
                    occupied_space += 50
                for animal in self.__outer._ecosystem.animal_map[x + dx][y + dy]:
                    occupied_space += animal.size
                from ecosystem import ANIMAL_CELL_CAPACITY
                if occupied_space + self.__outer.size > ANIMAL_CELL_CAPACITY:
                    self._status = bt.Status.FAIL
            else:
                self._status = bt.Status.SUCCESS
                self.__outer._movement_timer += self.__outer._movement_cooldown
                self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
                self.__outer.x += dx
                self.__outer.y += dy
                self.__outer._ecosystem.animal_map[x + dx][y + dy].append(self.__outer)
