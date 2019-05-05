import organisms
import behaviour_tree as bt
import earth

WATER_POOL_CAPACITY = 10000

class Water(organisms.Organism):
    """Defines the small water pool"""
    def __init__(self, ecosystem, x, y, amount=WATER_POOL_CAPACITY):
        super().__init__(ecosystem, organisms.Type.WATER, x, y)
        self._amount = amount

    def get_image(self):
        if self._amount < WATER_POOL_CAPACITY * 0.3:
            return 'images/waterLow.png'
        else:
            return 'images/waterHigh.png'

    def generate_tree(self):
        """Generates the tree for the water."""
        tree = bt.Sequence()
        dry_sequence = bt.Sequence()
        dry_sequence.add_child(self.IsDry(self))
        dry_sequence.add_child(self.DryOut(self))

        tree.add_child(dry_sequence)
        return tree


    class IsDry(bt.Condition):
        """Check if water pool is dry."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer._amount <= 0

    class DryOut(bt.Action):
        """Performs action when water pool is dried out"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            x = self.__outer.x
            y = self.__outer.y
            _earth = earth.Earth(self.__outer._ecosystem, x, y)
            self.__outer._ecosystem.water_map[x][y] = None
            self.__outer._ecosystem.plant_map[x][y] = _earth
            self._status = bt.Status.FAIL
