from enum import Enum
import math

def Lerp(min, max, fraction):
    return min + (max - min) * fraction

def InverseLerp(min, max, number):
    return (number - min)/ (max - min)

def EuclidianDistance(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def DirectionBetweenPoints(x1, y1, x2, y2):
    if x1 < x2:
        x_dir = 1
    elif x1 > x2:
        x_dir = -1
    else:
        x_dir = 0

    if y1 < y2:
        y_dir = 1
    elif y1 > y2:
        y_dir = -1
    else:
        y_dir = 0

    return x_dir, y_dir


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
