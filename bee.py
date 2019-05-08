import organisms
import random
import helpers
import behaviour_tree as bt

class Bee(organisms.Organism):
    """Defines the bee."""
    def __init__(self, ecosystem, x, y, hunger=0, tired=0, health=100, life_span=24*150,
                hunger_speed=50/36, tired_speed=50/36,
                vision_range={'left': 2, 'right': 2, 'up': 2, 'down': 2},
                smell_range={'left': 8, 'right': 8, 'up': 8, 'down': 8},
                hive=None, in_hive=False, movement_cooldown=4, age=0, scout=True):
        super().__init__(ecosystem, organisms.Type.BEE, x, y)

        self.size = 0

        self._hunger = hunger
        self._tired = tired
        self._health = health
        self._life_span = life_span
        self._hunger_speed = hunger_speed
        self._tired_speed = tired_speed
        self._hive = hive
        self.in_hive = in_hive
        self._movement_cooldown = movement_cooldown
        self._age = age

        self._movement_timer = self._movement_cooldown
        self._target_location = None
        self._food_location = None

        self._scout = scout
        self._vision_range = vision_range
        if scout:
            self._smell_range = smell_range
        else:
            smell_range = vision_range

    def get_image(self):
        return 'images/Bee.png'

    def generate_tree(self):
        """Generates the tree for the bee."""
        tree = bt.FallBack()

        is_dead_sequence = bt.Sequence()
        is_dead_sequence.add_child(self.Dying(self))
        is_dead_sequence.add_child(self.Die(self))

        sequence = bt.Sequence()
        logic_fallback = bt.FallBack()
        scout_sequence = bt.Sequence()
        logic_fallback.add_child(scout_sequence)
        scout_sequence.add_child(self.IsScout(self))
        scout_fallback = bt.FallBack()
        scout_sequence.add_child(scout_fallback)
        food_known_sequence = bt.Sequence()
        scout_sequence.add_child(food_known_sequence)
        food_known_fallback = bt.FallBack()
        food_known_sequence.add_child(food_known_fallback)
        in_hive_sequence = bt.Sequence()
        food_known_fallback.add_child(in_hive_sequence)
        # ADD GO TO HIVE


        search_food_sequence = bt.Sequence()
        scout_fallback.add_child(search_food_sequence)
        search_food_sequence.add_child(self.ShouldScoutForFood(self))

        scout_food_fallback = bt.FallBack()
        search_food_sequence.add_child(scout_food_fallback)

        # TODO: FIX
        see_food_sequence = bt.Sequence()

        smell_food_sequence = bt.Sequence()
        smell_food_sequence.add_child(self.FindBestSmell(self))
        smell_food_sequence.add_child(self.FlyToTargetLocation(self))

        random_movement_sequence = bt.Sequence()

        scout_food_fallback.add_child(smell_food_sequence)


        sequence.add_child(self.ReduceMovementTimer(self))
        sequence.add_child(self.IncreaseAge(self))
        sequence.add_child(logic_fallback)

        tree.add_child(is_dead_sequence)
        tree.add_child(sequence)
        return tree


    class Dying(bt.Condition):
        """Check if the bee is dying."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._health <= 0 or self.__outer._age >= self.__outer._life_span

    class Die(bt.Action):
        """Kill the bee."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
            self._status = bt.Status.SUCCESS



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


    class IncreaseAge(bt.Action):
        """Ticks down the movement timer for the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            # TODO: change size according to age
            self.__outer._age += 1
            self._status = bt.Status.SUCCESS


    #####################
    # SCOUT BEES #
    #####################


    class IsScout(bt.Condition):
        """Checks if the bee is a scout."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._scout

    class ShouldScoutForFood(bt.Condition):
        """Checks if the bee should scout."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return True

    class KnowWhereFoodIs(bt.Condition):
        """Checks if the bee scout knows where the food is."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._food_location is not None


    class InHive(bt.Condition):
        """Checks if the bee is in hive"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.in_hive

    class FindBestSmell(bt.Action):
        """Ticks down the movement timer for the rabbit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            smell_range = self.__outer._smell_range
            ecosystem = self.__outer._ecosystem
            best_smell = 0
            best_smell_location = None
            for dx in range(-int(smell_range['left']), int(smell_range['right'])+1):
                for dy in range(-int(smell_range['up']), int(smell_range['down'])+1):
                    if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                        continue
                    if  ecosystem.nectar_smell_map[x + dx][y + dy] > best_smell:
                        best_smell = ecosystem.nectar_smell_map[x + dx][y + dy]
                        best_smell_location = (x + dx, y + dy)

            if best_smell_location:
                self.__outer._target_location = best_smell_location
                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL


    class FlyToTargetLocation(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):

            x = self.__outer.x
            y = self.__outer.y
            target_location = self.__outer._target_location
            if random.random() <= 0.5:
                random_dir = random.choice(list(helpers.Direction))
                dx = random_dir.value[0]
                dy = random_dir.value[1]
            else:
                dx, dy = helpers.DirectionBetweenPoints(x, y, target_location[0], target_location[1])

            if x + dx < 0 or x + dx >= self.__outer._ecosystem.width or y + dy < 0 or y + dy >= self.__outer._ecosystem.height:
                self._status = bt.Status.FAIL
            else:
                self.__outer._movement_timer += self.__outer._movement_cooldown
                self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
                self.__outer.x += dx
                self.__outer.y += dy
                self.__outer._ecosystem.animal_map[x + dx][y + dy].append(self.__outer)
                self._status = bt.Status.SUCCESS

    class CanMove(bt.Condition):
        """Checks if the bee can move."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._movement_timer == 0
