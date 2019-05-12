import organisms
import behaviour_tree as bt
import helpers
import random
import math
from astar import astar
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
fox_HUNGER_SATISFACTION = 100
fox_SIZE_FACTOR = 1/20
WATER_DRINKING_AMOUNT = 0.00001 * WATER_POOL_CAPACITY

EATING_AND_DRINKING_SLEEP_FACTOR = 0.3
SLEEP_TIME = 10

HEAL_AMOUNT = 4

REPRODUCTION_TIME = 24*70 # foxs are pregnant for 70 days
REPRODUCTION_COOLDOWN = 24*180 # foxs usually mate once per year, we double that
NEW_BORN_TIME = 24*35
# TODO: Add new born follow mom time, about four months
NURSE_COOLDOWN = 24

class Fox(organisms.Organism):
    """Defines the fox."""
    def __init__(self, ecosystem, x, y, female, adult=False, hunger=0,
                 thirst=0, tired=0, health=100, size=35, life_span=24*365*5,
                 hunger_speed=50/36, thirst_speed=50/72, tired_speed=50/36,
                 vision_range={'left': 4, 'right': 4, 'up': 4, 'down': 4},
                 den=None, in_den=False, movement_cooldown=2, age=0):
        super().__init__(ecosystem, organisms.Type.FOX, x, y)
        self.female = female
        self._adult = adult

        self._hunger = hunger
        self._thirst = thirst
        self._tired = tired
        self._health = health
        self._life_span = life_span
        self.age = age
        self._hunger_speed = hunger_speed
        self._thirst_speed = thirst_speed
        self._tired_speed = tired_speed
        self._needs_to_poop = False
        self._poop_contains_seed = False

        if self._adult:
            self.size = size
            self._max_size = size
            self._vision_range = vision_range
            self._max_vision_range = vision_range
        else:
            self.size = 1
            self._max_size = size
            self._vision_range = {
                'left': 0,
                'right': 0,
                'up': 0,
                'down': 0
            }
            self._max_vision_range = vision_range


        # TODO:
        #     * Genetic variables

        self.can_reproduce = self._adult
        self.pregnant = False
        self.partner = None
        self.reproduction_timer = 0
        self._stabilized_health = False
        self._nurse_timer = 0
        self._stop_nursing_timer = 0

        self.den = den
        self.in_den = False

        self._asleep = False
        self._sleep_time = 0

        if self._adult:
            self._movement_cooldown = movement_cooldown
            self._min_movement_cooldown = movement_cooldown
        else:
            self._movement_cooldown = 2 * movement_cooldown
            self._min_movement_cooldown = movement_cooldown

        self._movement_timer = self._movement_cooldown
        self._movement_path = None


    def get_image(self):
        if self._adult:
            return 'images/foxAdult.png'
        else:
            return 'images/foxYoung.png'


    def generate_tree(self):
        """Generates the tree for the fox."""
        tree = bt.Sequence()
        tree.add_child(self.ReduceMovementTimer(self))
        tree.add_child(self.ReduceReproductionTimer(self))
        tree.add_child(self.DenMovement(self))

        # TEMPORARILY DISABLED TO ALLOW FOR TESTING OF OTHER THINGS
        #tree.add_child(self.IncreaseHunger(self))

        tree.add_child(self.IncreaseThirst(self))
        tree.add_child(self.ChangeTired(self))
        tree.add_child(self.HandleNursing(self))
        tree.add_child(self.IncreaseAge(self))
        tree.add_child(self.TakeDamage(self))
        tree.add_child(self.ReplenishHealth(self))

        # Logic for the fox
        logic_fallback = bt.FallBack()
        tree.add_child(logic_fallback)

        # Dying
        die_sequence = bt.Sequence()
        logic_fallback.add_child(die_sequence)
        die_sequence.add_child(self.Dying(self))
        die_sequence.add_child(self.Die(self))

        # New born
        logic_fallback.add_child(self.NewBorn(self))
        # TODO: Implement it.

        # Eating

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
        # Might want foxes to only know about water they've seen,
        # instead of knowing about water globally
        water_nearby_sequence.add_child(self.CanMove(self))
        water_nearby_sequence.add_child(self.FindPathToWater(self))
        water_nearby_sequence.add_child(self.MoveOnPath(self))

        # Sleeping
        sleep_sequence = bt.Sequence()
        logic_fallback.add_child(sleep_sequence)
        sleep_sequence.add_child(self.Sleeping(self))

        sleep_fallback = bt.FallBack()
        sleep_sequence.add_child(sleep_fallback)
        sleep_fallback.add_child(self.ShouldNotWakeUp(self))
        sleep_fallback.add_child(self.WakeUp(self))

        # Tiredness
        tired_sequence = bt.Sequence()
        logic_fallback.add_child(tired_sequence)
        tired_sequence.add_child(self.Tired(self))
        tired_sequence.add_child(self.Sleep(self))

        # Nursing
        nurse_sequence = bt.Sequence()
        logic_fallback.add_child(nurse_sequence)
        nurse_sequence.add_child(self.ShouldNurse(self))

        nurse_fallback = bt.FallBack()
        nurse_sequence.add_child(nurse_fallback)

        burrow_nurse_sequence = bt.Sequence()
        nurse_fallback.add_child(burrow_nurse_sequence)
        burrow_nurse_sequence.add_child(self.InDen(self))
        burrow_nurse_sequence.add_child(self.Nurse(self))

        move_to_burrow_nurse_sequence = bt.Sequence()
        nurse_fallback.add_child(move_to_burrow_nurse_sequence)
        move_to_burrow_nurse_sequence.add_child(self.CanMove(self))
        move_to_burrow_nurse_sequence.add_child(self.FindPathToDen(self))
        move_to_burrow_nurse_sequence.add_child(self.MoveOnPath(self))

        # Giving birth
        birth_sequence = bt.Sequence()
        logic_fallback.add_child(birth_sequence)
        birth_sequence.add_child(self.Pregnant(self))

        birth_fallback = bt.FallBack()
        birth_sequence.add_child(birth_fallback)

        birth_time_sequence = bt.Sequence()
        birth_fallback.add_child(birth_time_sequence)
        birth_time_sequence.add_child(self.TimeToGiveBirth(self))
        birth_time_sequence.add_child(self.GiveBirth(self))

        close_to_birth_sequence = bt.Sequence()
        birth_fallback.add_child(close_to_birth_sequence)
        close_to_birth_sequence.add_child(self.CloseToBirth(self))

        close_to_birth_fallback = bt.FallBack()
        close_to_birth_sequence.add_child(close_to_birth_fallback)
        close_to_birth_fallback.add_child(self.InDen(self))

        close_to_birth_burrow_sequence = bt.Sequence()
        close_to_birth_fallback.add_child(close_to_birth_burrow_sequence)
        close_to_birth_burrow_sequence.add_child(self.StabilizeHealth(self))
        close_to_birth_burrow_sequence.add_child(self.CreateDen(self))

        # Reproducing
        reproduction_sequence = bt.Sequence()
        logic_fallback.add_child(reproduction_sequence)
        reproduction_sequence.add_child(self.CanReproduce(self))

        reproduction_fallback = bt.FallBack()
        reproduction_sequence.add_child(reproduction_fallback)

        partner_sequence = bt.Sequence()
        reproduction_fallback.add_child(partner_sequence)
        partner_sequence.add_child(self.HavePartner(self))
        partner_sequence.add_child(self.PartnerCanReproduce(self))

        partner_reproduction_fallback = bt.FallBack()
        partner_sequence.add_child(partner_reproduction_fallback)

        partner_adjacent_sequence = bt.Sequence()
        partner_reproduction_fallback.add_child(partner_adjacent_sequence)
        partner_adjacent_sequence.add_child(self.PartnerAdjacent(self))
        partner_adjacent_sequence.add_child(self.Reproduce(self))

        partner_nearby_sequence = bt.Sequence()
        partner_reproduction_fallback.add_child(partner_nearby_sequence)
        partner_nearby_sequence.add_child(self.PartnerNearby(self))
        partner_nearby_sequence.add_child(self.CanMove(self))
        partner_nearby_sequence.add_child(self.FindPathToPartner(self))
        partner_nearby_sequence.add_child(self.MoveOnPath(self))

        no_partner_sequence = bt.Sequence()
        reproduction_fallback.add_child(no_partner_sequence)
        no_partner_sequence.add_child(self.NoPartner(self))

        no_partner_fallback = bt.FallBack()
        no_partner_sequence.add_child(no_partner_fallback)

        adjacent_fox_sequence = bt.Sequence()
        no_partner_fallback.add_child(adjacent_fox_sequence)
        adjacent_fox_sequence.add_child(self.AvailableFoxAdjacent(self))
        adjacent_fox_sequence.add_child(self.MakePartner(self))
        adjacent_fox_sequence.add_child(self.Reproduce(self))

        fox_nearby_sequence = bt.Sequence()
        no_partner_fallback.add_child(fox_nearby_sequence)
        fox_nearby_sequence.add_child(self.AvailableFoxNearby(self))
        fox_nearby_sequence.add_child(self.CanMove(self))
        fox_nearby_sequence.add_child(self.FindPathToFox(self))
        fox_nearby_sequence.add_child(self.MoveOnPath(self))

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
        """Ticks down the movement timer for the fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._movement_timer = max(0, self.__outer._movement_timer - 1)
            self._status = bt.Status.SUCCESS

    class ReduceReproductionTimer(bt.Action):
        """Ticks down the reproduction timer for the fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer.reproduction_timer = max(0, self.__outer.reproduction_timer - 1)
            if self.__outer.reproduction_timer == 0 and self.__outer._adult:
                self.__outer.can_reproduce = True
            self._status = bt.Status.SUCCESS

    class DenMovement(bt.Action):
        """Updates whether the fox is in its den or not."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            den = self.__outer.den

            if den is None:
                self.__outer.in_den = False
            else:
                self.__outer.in_den = (x == den.x and y == den.y)
            self._status = bt.Status.SUCCESS

    class IncreaseHunger(bt.Action):
        """Increases the fox's hunger."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            factor = 1 if not self.__outer._asleep else EATING_AND_DRINKING_SLEEP_FACTOR
            if not self.__outer._stabilized_health:
                self.__outer._hunger += factor * self.__outer._hunger_speed
            self._status = bt.Status.SUCCESS

    class IncreaseThirst(bt.Action):
        """Increases the fox's thirst."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            factor = 1 if not self.__outer._asleep else EATING_AND_DRINKING_SLEEP_FACTOR
            if not self.__outer._stabilized_health:
                self.__outer._thirst += factor * self.__outer._thirst_speed
            self._status = bt.Status.SUCCESS

    class ChangeTired(bt.Action):
        """Changes the fox's tiredness depending on if it is awake."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            if not self.__outer._asleep:
                if not self.__outer._stabilized_health:
                    self.__outer._tired += self.__outer._tired_speed
            else:
                self.__outer._tired = max(0, self.__outer._tired - TIRED_DAMAGE_THRESHOLD / SLEEP_TIME)
                self.__outer._sleep_time += 1
            self._status = bt.Status.SUCCESS

    class HandleNursing(bt.Action):
        """Handles nursing variables."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            if self.__outer.female:
                if self.__outer._stop_nursing_timer > 0:
                    self.__outer._stop_nursing_timer = max(0, self.__outer._stop_nursing_timer - 1)
                    self.__outer._nurse_timer = max(0, self.__outer._nurse_timer - 1)
            self._status = bt.Status.SUCCESS

    class IncreaseAge(bt.Action):
        """Increases the fox's age."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer.age += 1
            adult_age = 24*300

            # Become adults
            if not self.__outer._adult and self.__outer.age >= adult_age:
                self.__outer._adult = True
                self.__outer.can_reproduce = True
                self.__outer.size = self.__outer._max_size
                self.__outer._vision_range = self.__outer._max_vision_range
                self.__outer._movement_cooldown = self.__outer._min_movement_cooldown

            # Lerp values depending on age
            if not self.__outer._adult:
                self.__outer.size = helpers.Lerp(0, self.__outer._max_size, self.__outer.age / (adult_age))
                for key in self.__outer._vision_range:
                    self.__outer._vision_range[key] = min(self.__outer._max_vision_range[key], helpers.Lerp(0, self.__outer._max_vision_range[key], self.__outer.age / (NEW_BORN_TIME)))
                self.__outer._movement_cooldown = helpers.Lerp(2 * self.__outer._min_movement_cooldown, self.__outer._min_movement_cooldown, self.__outer.age / (adult_age))


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
                self.__outer._health -= (thirst - THIRST_DAMAGE_THRESHOLD) * THIRST_DAMAGE_FACTOR

            # Tiredness
            tired = self.__outer._tired
            if tired >= TIRED_DAMAGE_THRESHOLD:
                self.__outer._health -= (tired - TIRED_DAMAGE_THRESHOLD) * TIRED_DAMAGE_FACTOR

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

            if hunger < HUNGER_SEEK_THRESHOLD and thirst < THIRST_SEEK_THRESHOLD and tired < TIRED_SEEK_THRESHOLD and self.__outer._health > 0:
                self.__outer._health = min(100, self.__outer._health + HEAL_AMOUNT)

    #########
    # DYING #
    #########

    class Dying(bt.Condition):
        """Check if the fox is dying."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._health <= 0 or self.__outer.age >= self.__outer._life_span

    class Die(bt.Action):
        """Kill the fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
            self._status = bt.Status.SUCCESS

    ############
    # NEW BORN #
    ############

    class NewBorn(bt.Condition):
        """Check if the fox is newly born."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.age <= NEW_BORN_TIME

    ############
    # SLEEPING #
    ############

    class Sleeping(bt.Condition):
        """Determines if the fox is sleeping or not."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._asleep

    class ShouldNotWakeUp(bt.Condition):
        """Determines if the fox should continue to sleep."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._sleep_time < SLEEP_TIME

    class WakeUp(bt.Action):
        """Wakes up the fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._asleep = False
            self.__outer._sleep_time = 0
            self._status = bt.Status.SUCCESS

    class CanMove(bt.Condition):
        """Check if the fox can move."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._movement_timer == 0

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
                ecosystem = self.__outer._ecosystem
                if helpers.EuclidianDistance(self.__outer.x, self.__outer.y, x, y) <= 2:
                    self._status = bt.Status.SUCCESS
                    self.__outer._movement_timer += self.__outer._movement_cooldown
                    index = ecosystem.animal_map[self.__outer.x][self.__outer.y].index(self.__outer)
                    self.__outer._ecosystem.animal_map[x][y].append(ecosystem.animal_map[self.__outer.x][self.__outer.y].pop(index))
                    self.__outer.x = x
                    self.__outer.y = y
                else:
                    self._status = bt.Status.FAIL

    ##########
    # THIRST #
    ##########

    class ThirstierThanTired(bt.Condition):
        """Check if the fox is thirstier than it is tired."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._thirst >= self.__outer._tired

    class Thirsty(bt.Condition):
        """Check if the fox is thirsty."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return not self.__outer._stabilized_health and self.__outer._thirst >= THIRST_SEEK_THRESHOLD

    class WaterAdjacent(bt.Condition):
        """Check if there is water next to the fox."""
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

    #############
    # TIREDNESS #
    #############

    class Tired(bt.Condition):
        """Determines if the fox is tired."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return not self.__outer._stabilized_health and self.__outer._tired >= TIRED_SEEK_THRESHOLD

    class Sleep(bt.Action):
        """Fox goes to sleep."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._asleep = True
            self._status = bt.Status.SUCCESS

    ###########
    # NURSING #
    ###########

    class ShouldNurse(bt.Condition):
        """Determines if the fox should nurse its children or not."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            den = self.__outer.den

            if den is not None:
                # Should nurse if the time it takes to reach den is what's left
                # on the timer.
                distance = helpers.EuclidianDistance(x, y, den.x, den.y)
                nurse_timer = self.__outer._nurse_timer
                return distance >= nurse_timer
            else:
                return False

    class Nurse(bt.Action):
        """The fox nurses its children."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            self.__outer._nurse_timer = NURSE_COOLDOWN

            for animal in ecosystem.animal_map[x][y]:
                if animal.type == organisms.Type.FOX and animal.age <= NEW_BORN_TIME:
                    animal._hunger = 0
                    animal._thirst = 0
                    animal._tired = 0

            self._status = bt.Status.SUCCESS

    class FindPathToDen(bt.Action):
        """Finds a path to the fox's den."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            den = self.__outer.den
            vision_range = self.__outer._vision_range
            ecosystem = self.__outer._ecosystem

            path = []
            if den is not None:
                path = astar(self.__outer, ecosystem.water_map, ecosystem.plant_map, ecosystem.animal_map,
                             x, y, den.x, den.y, max_path_length=10)

            if len(path) > 0:
                path.pop(0)
                self.__outer._movement_path = path
                self._status = bt.Status.SUCCESS
            else:
                self.__outer._movement_path = None
                self._status = bt.Status.FAIL

    ################
    # GIVING BIRTH #
    ################

    class Pregnant(bt.Condition):
        """Determines if the fox is pregnant or not."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.pregnant

    class TimeToGiveBirth(bt.Condition):
        """Determines if the time has come to give birth."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.reproduction_timer <= REPRODUCTION_COOLDOWN

    class GiveBirth(bt.Action):
        """The fox gives birth."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._stabilized_health = False
            self.__outer.pregnant = False
            self.__outer._stop_nursing_timer = NEW_BORN_TIME
            self.__outer._nurse_timer = 0

            minimum_amount = 4
            maximum_amount = 6

            x = self.__outer.x
            y = self.__outer.y
            den = self.__outer.den
            ecosystem = self.__outer._ecosystem

            if den is not None:
                for _ in range(random.randint(minimum_amount, maximum_amount)):
                    gender = random.choice([True, False])
                    fox = Fox(ecosystem, x, y, gender, adult=False, den=den, in_den=True)
                    ecosystem.animal_map[x][y].append(fox)

                self._status = bt.Status.SUCCESS
            else:
                self._status = bt.Status.FAIL

    class CloseToBirth(bt.Condition):
        """Determines if the fox is about to give birth."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.reproduction_timer <= REPRODUCTION_COOLDOWN + 24*2 # Two days prior to giving birth

    class InDen(bt.Condition):
        """Determines if the fox is in its burrow."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.in_den

    class StabilizeHealth(bt.Action):
        """Stabilizes the fox's health for the remainder of the pregnancy."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._stabilized_health = True
            self._status = bt.Status.SUCCESS

    class CreateDen(bt.Action):
        """The fox creates a new den."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            from den import Den

            if not self.__outer.in_den:
                x = self.__outer.x
                y = self.__outer.y
                den = Den(self.__outer._ecosystem, x, y)
                self.__outer._ecosystem.animal_map[x][y].insert(0, den)
                self.__outer.den = den

                # Increase hunger due to having to dig a hole
                if not self.__outer._stabilized_health:
                    self.__outer._hunger += 3 * self.__outer._hunger_speed
            self._status = bt.Status.SUCCESS

    ################
    # REPRODUCTION #
    ################

    class CanReproduce(bt.Condition):
        """Determines if the fox can reproduce."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.can_reproduce

    class HavePartner(bt.Condition):
        """Determines if the fox has a partner."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.partner is not None

    class PartnerCanReproduce(bt.Condition):
        """Determines if the fox's partner can reproduce."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.partner.can_reproduce

    class PartnerAdjacent(bt.Condition):
        """Determines if the partner is in the same cell as the fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            partner = self.__outer.partner

            return x == partner.x and y == partner.y

    class Reproduce(bt.Action):
        """The fox and its partner do the funky stuff."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            partner = self.__outer.partner

            if self.__outer.female:
                self.__outer.pregnant = True
                self.__outer.reproduction_timer = REPRODUCTION_COOLDOWN + REPRODUCTION_TIME
                self.__outer.can_reproduce = False
            else:
                partner.pregnant = True
                partner.reproduction_timer = REPRODUCTION_COOLDOWN + REPRODUCTION_TIME
                partner.can_reproduce = False
            self._status = bt.Status.SUCCESS

    class PartnerNearby(bt.Condition):
        """Determines if the fox's partner is within vision range."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            vision_range = self.__outer._vision_range
            ecosystem = self.__outer._ecosystem
            partner = self.__outer.partner

            for dx in range(-int(vision_range['left']), int(vision_range['right'])+1):
                for dy in range(-int(vision_range['up']), int(vision_range['down'])+1):
                    if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                        continue

                    if x + dx == partner.x and y + dy == partner.y:
                        return True
            return False

    class FindPathToPartner(bt.Action):
        """Finds a path to the fox's partner."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem
            partner = self.__outer.partner

            path = astar(self.__outer, ecosystem.water_map, ecosystem.plant_map, ecosystem.animal_map,
                         x, y, partner.x, partner.y, max_path_length=10)

            if len(path) > 0:
                path.pop(0)
                self.__outer._movement_path = path
                self._status = bt.Status.SUCCESS
            else:
                self.__outer._movement_path = None
                self._status = bt.Status.FAIL

    class NoPartner(bt.Condition):
        """Determines if the fox has no partner."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.partner is None

    class AvailableFoxAdjacent(bt.Condition):
        """Determines if there is a fox with no partner that can reproduce
        that is on the same cell as the fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            for animal in ecosystem.animal_map[x][y]:
                if animal is not self.__outer:
                    if animal.type == organisms.Type.FOX:
                        if not animal.partner and animal.can_reproduce and animal.female != self.__outer.female:
                            return True
            return False

    class MakePartner(bt.Action):
        """Make the available fox this fox's partner and vice versa."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem

            self._status = bt.Status.FAIL
            for animal in ecosystem.animal_map[x][y]:
                if animal is not self.__outer:
                    if animal.type == organisms.Type.FOX:
                        if not animal.partner and animal.can_reproduce and animal.female is not self.__outer.female:
                            self._status = bt.Status.SUCCESS
                            self.__outer.partner = animal
                            animal.partner = self.__outer

    class AvailableFoxNearby(bt.Condition):
        """Determines if there is a fox in this fox's vision range
        that can reproduce and has no partner."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            vision_range = self.__outer._vision_range
            ecosystem = self.__outer._ecosystem

            for dx in range(-int(vision_range['left']), int(vision_range['right'])+1):
                for dy in range(-int(vision_range['up']), int(vision_range['down'])+1):
                    if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                        continue

                    for animal in ecosystem.animal_map[x + dx][y + dy]:
                        if animal is not self.__outer:
                            if animal.type == organisms.Type.FOX:
                                if not animal.partner and animal.can_reproduce and animal.female is not self.__outer.female:
                                    return True
            return False

    class FindPathToFox(bt.Action):
        """Finds a path to the available fox."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            vision_range = self.__outer._vision_range
            ecosystem = self.__outer._ecosystem

            closest_rabbit = None
            best_distance = math.inf

            for dx in range(-int(vision_range['left']), int(vision_range['right'])+1):
                for dy in range(-int(vision_range['up']), int(vision_range['down'])+1):
                    if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                        continue

                    distance = helpers.EuclidianDistance(x, y, x + dx, y + dy)
                    if distance < best_distance:
                        for animal in ecosystem.animal_map[x + dx][y + dy]:
                            if animal is not self.__outer:
                                if animal.type == organisms.Type.FOX:
                                    if not animal.partner and animal.can_reproduce and animal.female is not self.__outer.female:
                                        closest_rabbit = animal
                                        best_distance = distance
                                        break

            path = astar(self.__outer, ecosystem.water_map, ecosystem.plant_map, ecosystem.animal_map,
                         x, y, closest_rabbit.x, closest_rabbit.y, max_path_length=10)

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
        """Moves the fox randomly."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            # TODO: Make excessive movement result in size decrease?
            x = self.__outer.x
            y = self.__outer.y
            ecosystem = self.__outer._ecosystem
            direction = random.choice(list(helpers.Direction))
            dx = direction.value[0]
            dy = direction.value[1]

            if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                self._status = bt.Status.FAIL
            elif ecosystem.water_map[x + dx][y + dy]:
                self._status = bt.Status.FAIL
            elif ecosystem.animal_map[x + dx][y + dy]:
                occupied_space = 0
                if ecosystem.plant_map[x + dx][y + dy] and ecosystem.plant_map[x + dx][y + dy].type == organisms.Type.TREE:
                    occupied_space += 50
                for animal in ecosystem.animal_map[x + dx][y + dy]:
                    occupied_space += animal.size
                from ecosystem import ANIMAL_CELL_CAPACITY
                if occupied_space + self.__outer.size > ANIMAL_CELL_CAPACITY:
                    self._status = bt.Status.FAIL
            else:
                self._status = bt.Status.SUCCESS
                self.__outer._movement_timer += self.__outer._movement_cooldown
                index = ecosystem.animal_map[x][y].index(self.__outer)
                ecosystem.animal_map[x + dx][y + dy].append(ecosystem.animal_map[x][y].pop(index))
                self.__outer.x += dx
                self.__outer.y += dy
