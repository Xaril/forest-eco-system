import organisms
import behaviour_tree as bt
import earth
from helpers import Direction
import constants

WATER_POOL_CAPACITY = 10000

class Water(organisms.Organism):
    """Defines the small water pool"""
    def __init__(self, ecosystem, x, y, amount=WATER_POOL_CAPACITY):
        super().__init__(ecosystem, organisms.Type.WATER, x, y)
        self.water_amount = amount

        self.water_capacity = WATER_POOL_CAPACITY

    def get_image(self):
        if self.water_amount < WATER_POOL_CAPACITY * 0.3:
            return 'images/waterLow.png'
        else:
            return 'images/waterHigh.png'

    def generate_tree(self):
        """Generates the tree for the water."""
        tree = bt.FallBack()
        dry_sequence = bt.Sequence()
        dry_sequence.add_child(self.IsDry(self))
        dry_sequence.add_child(self.DryOut(self))

        tree.add_child(dry_sequence)
        tree.add_child(self.MoveWater(self))
        return tree


    class IsDry(bt.Condition):
        """Check if water pool is dry."""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def condition(self):
            return self.__outer.water_amount <= 0

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

    class MoveWater(bt.Action):
        """Simulater subterranean water movements"""
        def __init__(self, outer):
            super().__init__()
            self.__outer = outer

        def action(self):
            directions = list(Direction)
            cells_to_add_water = []
            total_water_amount = 0

            spilling_over = self.__outer.water_amount > self.__outer.water_capacity
            min_water_cell = self.__outer
            for dir in directions:
                x = self.__outer.x + dir.value[0]
                y = self.__outer.y + dir.value[1]

                # check if in bounds
                if x < 0 or x >= self.__outer._ecosystem.width or y < 0 or y >= self.__outer._ecosystem.height:
                    continue

                cell = self.__outer._ecosystem.plant_map[x][y]
                if not cell:
                    cell = self.__outer._ecosystem.water_map[x][y]
                if cell and cell.type != organisms.Type.TREE:
                    cells_to_add_water.append(cell)
                    if cell.water_amount < min_water_cell.water_amount:
                        min_water_cell = cell


            if spilling_over:
                water_over = (self.__outer.water_amount - self.__outer.water_capacity) / len(cells_to_add_water)
                for cell in cells_to_add_water:
                    if cell.type == organisms.Type.WATER:
                        water_moved = water_over * constants.WATER_TO_WATER_MOVE_SPEED
                    elif cell.type == organisms.Type.EARTH:
                        water_moved = water_over * constants.WATER_TO_WATER_MOVE_SPEED
                    elif cell.type == organisms.Type.GRASS:
                        water_moved = water_over * constants.WATER_TO_GRASS_MOVE_SPEED

                    self.__outer.water_amount -= water_moved
                    cell.water_amount += water_moved
            else:
                water_diff = (self.__outer.water_amount - min_water_cell.water_amount) / 2
                if min_water_cell.type == organisms.Type.EARTH:
                    moved_water = min(water_diff  * constants.WATER_TO_EARTH_WATER_MOVE_SPEED, (min_water_cell.water_capacity - min_water_cell.water_amount) * 0.1)
                elif min_water_cell.type == organisms.Type.GRASS:
                    moved_water = min(water_diff  * constants.WATER_TO_GRASS_WATER_MOVE_SPEED, (min_water_cell.water_capacity - min_water_cell.water_amount) * 0.1)
                else:
                    moved_water = water_diff

                self.__outer.water_amount -= moved_water
                min_water_cell.water_amount += moved_water



            self._status = bt.Status.SUCCESS
