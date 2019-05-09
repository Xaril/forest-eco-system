import organisms
import random
import helpers
import behaviour_tree as bt


BEE_MIN_NECTAR_IN_FLOWER = 5

class Bee(organisms.Organism):
    """Defines the bee."""
    def __init__(self, ecosystem, x, y, hunger=0, tired=0, health=100, life_span=24*150,
                hunger_speed=50/36, tired_speed=50/36,
                vision_range={'left': 1, 'right': 1, 'up': 1, 'down': 1},
                smell_range={'left': 8, 'right': 8, 'up': 8, 'down': 8},
                hive=None, in_hive=False, movement_cooldown=2, age=0, scout=False,
                nectar_capacity=0.5):
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
        self._nectar_amount = 0
        self._nectar_capacity = nectar_capacity

        self._movement_timer = self._movement_cooldown
        self._target_location = None
        self.food_location = None
        self._flower_to_harvest = None

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
        recruit_sequence = bt.Sequence()
        logic_fallback.add_child(scout_sequence)
        logic_fallback.add_child(recruit_sequence)

        # Scout

        scout_sequence.add_child(self.IsScout(self))
        scout_fallback = bt.FallBack()
        scout_sequence.add_child(scout_fallback)
        food_known_sequence = bt.Sequence()
        scout_fallback.add_child(food_known_sequence)
        food_known_fallback = bt.FallBack()
        food_known_sequence.add_child(self.KnowWhereFoodIs(self))
        food_known_sequence.add_child(food_known_fallback)
        in_hive_sequence = bt.Sequence()
        in_hive_sequence.add_child(self.InHive(self))
        in_hive_sequence.add_child(self.AvailableRecruits(self))
        in_hive_sequence.add_child(self.SendRecruits(self))
        food_known_fallback.add_child(in_hive_sequence)
        fly_to_hive_sequence = bt.Sequence()
        fly_to_hive_sequence.add_child(self.NotInHive(self))
        fly_to_hive_sequence.add_child(self.SetHiveTargetLocation(self))
        fly_to_hive_sequence.add_child(self.CanMove(self))
        fly_to_hive_sequence.add_child(self.FlyToTargetLocation(self))
        food_known_fallback.add_child(fly_to_hive_sequence)


        search_food_sequence = bt.Sequence()
        scout_fallback.add_child(search_food_sequence)
        search_food_sequence.add_child(self.DontKnowAboutFood(self))
        search_food_sequence.add_child(self.ShouldScoutForFood(self))

        scout_food_fallback = bt.FallBack()
        search_food_sequence.add_child(scout_food_fallback)


        can_see_food_sequence = bt.Sequence()
        can_see_food_sequence.add_child(self.CanSeeFood(self))

        smell_food_sequence = bt.Sequence()
        smell_food_sequence.add_child(self.FindBestSmell(self))
        smell_food_sequence.add_child(self.CanMove(self))
        smell_food_sequence.add_child(self.FlyToTargetLocation(self))

        random_movement_sequence = bt.Sequence()
        random_movement_sequence.add_child(self.CanMove(self))
        random_movement_sequence.add_child(self.FlyRandomly(self))

        scout_food_fallback.add_child(smell_food_sequence)
        scout_food_fallback.add_child(random_movement_sequence)
        scout_food_fallback.add_child(can_see_food_sequence)

        # Recruit
        recruit_sequence.add_child(self.IsRecruit(self))
        recruit_fallback = bt.FallBack()
        recruit_sequence.add_child(recruit_fallback)

        ## Collect nectar
        on_food_target_sequence = bt.Sequence()
        on_food_target_sequence.add_child(self.IsOnFoodTargetLocation(self))
        on_food_target_fallback = bt.FallBack()
        on_food_target_sequence.add_child(on_food_target_fallback)
        location_have_nectar_sequence = bt.Sequence()
        on_food_target_fallback.add_child(location_have_nectar_sequence)
        location_have_nectar_sequence.add_child(self.HaveTargetLocationNectar(self))
        location_have_nectar_sequence.add_child(self.TakeNectar(self))
        on_food_target_fallback.add_child(self.RemoveFoodTargetLocation(self))
        recruit_fallback.add_child(on_food_target_sequence)

        ## Have nectar

        have_nectar_sequence = bt.Sequence()
        have_nectar_sequence.add_child(self.HaveFood(self))
        have_nectar_fallback = bt.FallBack()
        have_nectar_sequence.add_child(have_nectar_fallback)
        recruit_in_hive_sequence = bt.Sequence()
        have_nectar_fallback.add_child(recruit_in_hive_sequence)
        recruit_in_hive_sequence.add_child(self.InHive(self))
        recruit_in_hive_sequence.add_child(self.LeaveFoodInHive(self))
        move_to_hive_sequence = bt.Sequence()
        move_to_hive_sequence.add_child(self.SetHiveTargetLocation(self))
        move_to_hive_sequence.add_child(self.CanMove(self))
        move_to_hive_sequence.add_child(self.FlyToTargetLocation(self))
        have_nectar_fallback.add_child(move_to_hive_sequence)

        recruit_no_food_fallback = bt.FallBack()
        recruit_know_food_sequence = bt.Sequence()
        recruit_no_food_fallback.add_child(recruit_know_food_sequence)
        recruit_know_food_sequence.add_child(self.KnowWhereFoodIs(self))
        recruit_know_food_sequence.add_child(self.SetFoodAsTarget(self))
        recruit_know_food_sequence.add_child(self.CanMove(self))
        recruit_know_food_sequence.add_child(self.FlyToTargetLocation(self))

        recruit_dont_know_food_sequence = bt.Sequence()
        recruit_dont_know_food_sequence.add_child(self.NotInHive(self))
        recruit_dont_know_food_sequence.add_child(self.DontKnowAboutFood(self))
        recruit_dont_know_food_sequence.add_child(self.SetHiveTargetLocation(self))
        recruit_dont_know_food_sequence.add_child(self.CanMove(self))
        recruit_dont_know_food_sequence.add_child(self.FlyToTargetLocation(self))

        recruit_fallback.add_child(have_nectar_sequence)
        recruit_fallback.add_child(recruit_no_food_fallback)
        recruit_fallback.add_child(recruit_dont_know_food_sequence)





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
            return self.__outer.food_location is not None


    class InHive(bt.Condition):
        """Checks if the bee is in hive"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.in_hive

    class NotInHive(bt.Condition):
        """Checks if the bee is in hive"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return not self.__outer.in_hive

    class DontKnowAboutFood(bt.Condition):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.food_location is None


    class AvailableRecruits(bt.Condition):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            hive = self.__outer._hive
            ecosystem = self.__outer._ecosystem
            for animal in ecosystem.animal_map[hive.x][hive.y]:
                if animal.type == organisms.Type.BEE and animal._hive == hive and not animal.food_location:
                    return True
            return False


    class SendRecruits(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            hive = self.__outer._hive
            ecosystem = self.__outer._ecosystem
            for animal in ecosystem.animal_map[hive.x][hive.y]:
                if animal.type == organisms.Type.BEE and animal._hive == hive and not animal.food_location:
                    animal.food_location = self.__outer.food_location
            self.__outer.food_location = None
            self._status = bt.Status.SUCCESS


    class SetHiveTargetLocation(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            hive = self.__outer._hive
            self.__outer._target_location = (hive.x, hive.y)
            self._status = bt.Status.SUCCESS


    class IsRecruit(bt.Condition):
        """Checks if the bee is a recruit."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return not self.__outer._scout


    class HaveFood(bt.Condition):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._nectar_amount > 0

    class LeaveFoodInHive(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._hive.food += self.__outer._nectar_amount
            self.__outer._nectar_amount = 0
            self._status = bt.Status.SUCCESS


    class IsOnFoodTargetLocation(bt.Condition):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y

            if not self.__outer.food_location:
                return False

            target_x, target_y = self.__outer.food_location
            return x == target_x and y == target_y


    class HaveTargetLocationNectar(bt.Condition):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            target_x, target_y = self.__outer.food_location

            if not self.__outer._ecosystem.flower_map[target_x][target_y]:
                return False

            best_flower = None
            best_flower_nectar = 0
            for flower in self.__outer._ecosystem.flower_map[target_x][target_y]:
                if flower.nectar >= BEE_MIN_NECTAR_IN_FLOWER and flower.nectar > best_flower_nectar:
                    best_flower = flower
                    best_flower_nectar = flower.nectar

            self.__outer._flower_to_harvest = best_flower
            return best_flower is not None

    class TakeNectar(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            flower = self.__outer._flower_to_harvest
            self.__outer._nectar_amount = self.__outer._nectar_capacity
            flower.nectar -= self.__outer._nectar_capacity
            self._status = bt.Status.SUCCESS

    class RemoveFoodTargetLocation(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._flower_to_harvest = None
            self.__outer.food_location = None
            self._status = bt.Status.SUCCESS

    class CanSeeFood(bt.Condition):
        """Checks if the bee is in hive"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            x = self.__outer.x
            y = self.__outer.y
            vision_range = self.__outer._vision_range
            ecosystem = self.__outer._ecosystem
            best_smell = 0
            best_smell_location = None
            for dx in range(-int(vision_range['left']), int(vision_range['right'])+1):
                for dy in range(-int(vision_range['up']), int(vision_range['down'])+1):
                    if x + dx < 0 or x + dx >= ecosystem.width or y + dy < 0 or y + dy >= ecosystem.height:
                        continue
                    if ecosystem.flower_map[x + dx][y + dy]:
                        self.__outer.food_location = (x + dx, y + dy)
                        self._status = bt.Status.SUCCESS
                        return
            self._status = bt.Status.FAIL


    class SetFoodAsTarget(bt.Action):
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            self.__outer._target_location = self.__outer.food_location
            self._status = bt.Status.SUCCESS


    class FindBestSmell(bt.Action):
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
            if random.random() <= 0:
                random_dir = random.choice(list(helpers.Direction))
                dx = random_dir.value[0]
                dy = random_dir.value[1]
            else:
                dx, dy = helpers.DirectionBetweenPoints(x, y, target_location[0], target_location[1])

            if x + dx < 0 or x + dx >= self.__outer._ecosystem.width or y + dy < 0 or y + dy >= self.__outer._ecosystem.height:
                self._status = bt.Status.FAIL
            else:
                self._status = bt.Status.SUCCESS
                self.__outer._movement_timer += self.__outer._movement_cooldown
                self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
                self.__outer.x += dx
                self.__outer.y += dy
                self.__outer._ecosystem.animal_map[x + dx][y + dy].append(self.__outer)
                for animal in self.__outer._ecosystem.animal_map[x + dx][y + dy]:
                    if animal.type == organisms.Type.HIVE:
                        self.__outer.in_hive = True
                        return
                self.__outer.in_hive = False


    class CanMove(bt.Condition):
        """Checks if the bee can move."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._movement_timer == 0


    ###################
    # RANDOM MOVEMENT #
    ###################

    class FlyRandomly(bt.Action):
        """Moves the rabbit randomly."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            direction = random.choice(list(helpers.Direction))
            dx = direction.value[0]
            dy = direction.value[1]

            if x + dx < 0 or x + dx >= self.__outer._ecosystem.width or y + dy < 0 or y + dy >= self.__outer._ecosystem.height:
                self._status = bt.Status.FAIL
            else:
                self._status = bt.Status.SUCCESS
                self.__outer._movement_timer += self.__outer._movement_cooldown
                self.__outer._ecosystem.animal_map[x][y].remove(self.__outer)
                self.__outer.x += dx
                self.__outer.y += dy
                self.__outer._ecosystem.animal_map[x + dx][y + dy].append(self.__outer)
                for animal in self.__outer._ecosystem.animal_map[x + dx][y + dy]:
                    if animal.type == organisms.Type.HIVE:
                        self.__outer.in_hive = True
                        return
                self.__outer.in_hive = False
