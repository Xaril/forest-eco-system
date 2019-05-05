from enum import Enum
from abc import ABC, abstractmethod

class Status(Enum):
    """The different status codes when iterating through the behaviour tree."""
    SUCCESS = 0
    RUNNING = 1
    FAIL = 2


class Node(ABC):
    """An abstract class defining a node in the behaviour tree.
    Subclasses must implement the run function.
    """
    @abstractmethod
    def run(self):
        pass


class BehaviourTree(Node):
    """An abstract class defining non-leaf nodes in the behaviour tree.
    Subclasses must implement the run function.
    """
    def __init__(self):
        self._children = []

    @abstractmethod
    def run(self):
        pass

    def add_child(self, child):
        """Adds a child to the node of the tree"""
        if isinstance(child, Node):
            self._children.append(child)
        else:
            raise Exception('Behaviour tree nodes must be of Node type.')

    def insert_child(self, index, child):
        """Inserts a child at the given index at the node of the tree"""
        if isinstance(child, Node):
            self._children.insert(index, child)
        else:
            raise Exception('Behaviour tree nodes must be of Node type.')


class FallBack(BehaviourTree):
    """The fallback node in a behaviour tree."""
    def run(self):
        """Returns upon finding a success or running. Otherwise runs all
        children and returns fail.
        """
        for child in self._children:
            status = child.run()
            if status == Status.SUCCESS:
                return Status.SUCCESS
            elif status == Status.RUNNING:
                return Status.RUNNING
        return Status.FAIL


class Sequence(BehaviourTree):
    """The sequence node in a behaviour tree."""
    def run(self):
        """Returns upon finding a fail or running. Otherwise runs all children
        and returns success.
        """
        for child in self._children:
            status = child.run()
            if status == Status.FAIL:
                return Status.FAIL
            elif status == Status.RUNNING:
                return Status.RUNNING
        return Status.SUCCESS


class Condition(Node):
    """Defines a condition in the behaviour tree. Only checks if condition
    holds, and performs no state changes.
    """
    @abstractmethod
    def condition():
        pass

    def run(self):
        """Returns success if condition holds, and failure otherwise."""
        if self.condition():
            return Status.SUCCESS
        else:
            return Status.FAIL


class Action(Node):
    """Defines an action in the behaviour tree. Performs the action and returns
    the status.
    """
    def __init__(self):
        self._status = Status.RUNNING

    @abstractmethod
    def action():
        pass

    def run(self):
        """Depending on how the action changes the state, returns the status."""
        self.action()
        return self._status
