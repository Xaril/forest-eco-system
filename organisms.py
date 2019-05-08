from abc import ABC, abstractmethod
from enum import Enum
import behaviour_tree as bt


class Type(Enum):
    """The different types of organisms in the ecosystem."""
    EARTH = 0
    WATER = 1
    TREE = 2
    GRASS = 3
    FLOWER = 4
    RABBIT = 5
    BURROW = 6
    HIVE = 7


class Organism(ABC):
    """An abstract class container for organisms. Contains the tree for the
    organism. Subclasses must implement a tree generation function.
    """
    def __init__(self, ecosystem, type, x, y):
        self._ecosystem = ecosystem
        self.type = type
        self.x = x
        self.y = y
        self._tree = self.generate_tree()

    @abstractmethod
    def generate_tree(self):
        pass

    @abstractmethod
    def get_image(self):
        pass

    def run(self):
        """Runs the organism's behaviour tree and returns the result."""
        return self._tree.run()
