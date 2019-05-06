from enum import Enum

def Lerp(min, max, fraction):
    return min + (max - min) * fraction

def InverseLerp(min, max, number):
    return (number - min)/ (max - min)

class Direction(Enum):
    """The different directions."""
    CENTER = (0, 0)
    EAST = (1, 0)
    NORTH = (0, 1)
    NORTHEAST = (1, 1)
    NORTHWEST = (-1, 1)
    SOUTH = (0, -1)
    SOUTHEAST = (1, -1)
    SOUTHWEST = (-1, -1)
    WEST = (-1, 0)
