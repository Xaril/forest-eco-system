import organisms
import behaviour_tree as bt

class Fox(organisms.Organism):
    """Defines the fox."""
    def __init__(self, ecosystem, x, y, female, adult=False, hunger=0,
                 thirst=0, tired=0, health=100, size=20, life_span=24*365*5,
                 hunger_speed=50/36, thirst_speed=50/72, tired_speed=50/36,
                 vision_range={'left': 4, 'right': 4, 'up': 4, 'down': 4},
                 burrow=None, in_burrow=False, movement_cooldown=3, age=0):
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

        self.burrow = burrow
        self.in_burrow = False

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

        return tree
