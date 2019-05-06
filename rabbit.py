import organisms
import behaviour_tree as bt

HUNGER_SEEK_THRESHOLD = 50
THIRST_SEEK_THRESHOLD = 50
TIRED_SEEK_THRESHOLD = 50
HUNGER_DAMAGE_THRESHOLD = 90
THIRST_DAMAGE_THRESHOLD = 75
TIRED_DAMAGE_THRESHOLD = 80

REPRODUCTION_TIME = 24*30 # Rabbits are pregnant for 30 days
REPRODUCTION_COOLDOWN = 24*5 # Rabbits usually have to wait 5 days before being able to reproduce again


class Rabbit(organisms.Organism):
    """Defines the rabbit."""
    def __init__(self, ecosystem, x, y, female, adult=False, hunger=50,
                 thirst=0, tired=0, health=100, size=20, life_span=24*365*7,
                 hunger_speed=50/12, thirst_speed=50/24, tired_speed=50/12,
                 burrow=None):
        super().__init__(ecosystem, organisms.Type.RABBIT, x, y)
        self._female = female
        self._adult = adult

        self._hunger = hunger
        self._thirst = thirst
        self._tired = tired
        self._health = health
        self._size = size
        self._life_span = life_span
        self._hunger_speed = hunger_speed
        self._thirst_speed = thirst_speed
        self._tired_speed = tired_speed

        self._can_reproduce = self._adult
        self._pregnant = False
        self._partner = None

        self._burrow = burrow


    def get_image(self):
        if self._adult:
            return 'images/rabbitAdult.png'
        else:
            return 'images/rabbitYoung.png'


    def generate_tree(self):
        """Generates the tree for the rabbit."""
        tree = bt.FallBack()
        return tree
