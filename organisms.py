from abc import ABC, abstractmethod
from enum import Enum
import behaviour_tree as bt


class Type(Enum):
    """The different types of organisms in the ecosystem."""
    TREE = 0


class Organism(ABC):
    """An abstract class container for organisms. Contains the tree for the
    organism. Subclasses must implement a tree generation function.
    """
    def __init__(self, ecosystem, type, image, x, y):
        self._ecosystem = ecosystem
        self.type = type
        self.image = image
        self.x = x
        self.y = y

        self._tree = self.generate_tree()

    @abstractmethod
    def generate_tree(self):
        pass

    def run(self):
        """Runs the organism's behaviour tree and returns the result."""
        return self._tree.run()
