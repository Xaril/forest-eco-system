import helpers
import organisms
import sys
import math


directions = list(helpers.Direction)


class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, x=None, y=None):
        self.parent = parent
        self.x = x
        self.y = y

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return ((self.x == other.x) and (self.y == other.y))


def astar(traverser, water_map, plant_map, animal_map, start_x, start_y, end_x, end_y, max_path_length=math.inf):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    # Create start and end node
    start_node = Node(None, start_x, start_y)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end_x, end_y)
    end_node.g = end_node.h = end_node.f = 0


    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end

    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node or current_node.g > max_path_length :
            path = []
            current = current_node
            while current is not None:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        from ecosystem import ANIMAL_CELL_CAPACITY
        for dir in directions: # Adjacent squares

            # Get node position
            node_position_x = current_node.x + dir.value[0]
            node_position_y = current_node.y + dir.value[1]

            # Make sure within range
            width = len(water_map)
            height = len(water_map[0])
            if node_position_x >= width or node_position_x < 0 or node_position_y >= height or node_position_y < 0:
                continue

            # Make sure walkable terrain
            if water_map[node_position_x][node_position_y]:
                continue
            elif plant_map[node_position_x][node_position_y] and plant_map[node_position_x][node_position_y].type == organisms.Type.TREE:
                occupied_space = 50
                if animal_map[node_position_x][node_position_y]:
                    for animal in animal_map[node_position_x][node_position_y]:
                        occupied_space += animal.size
                if occupied_space + traverser.size > ANIMAL_CELL_CAPACITY:
                    continue
            elif animal_map[node_position_x][node_position_y]:
                occupied_space = 0
                for animal in animal_map[node_position_x][node_position_y]:
                    occupied_space += animal.size
                if occupied_space + traverser.size > ANIMAL_CELL_CAPACITY:
                    continue



            # Create new node
            new_node = Node(current_node, node_position_x, node_position_y)

            if new_node in closed_list:
                continue

            new_node.g = current_node.g + 1
            new_node.h = ((new_node.x - end_node.x) ** 2) + ((new_node.y - end_node.y) ** 2)
            new_node.f = new_node.g + new_node.h

            found_node = False
            for (index, node) in enumerate(open_list):
                if node == new_node:
                    found_node = True
                    if new_node.g < node.g:
                        open_list[index] = new_node
                    break

            if not found_node:
                open_list.append(new_node)

    return []
