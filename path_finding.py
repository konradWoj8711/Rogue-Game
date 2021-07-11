# Credit for this: Nicholas Swift
# as found at https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
from warnings import warn
import heapq

class Node:
    """
    A node class for A* Pathfinding
    """

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __repr__(self):
      return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

    # defining less than for purposes of heap queue
    def __lt__(self, other):
      return self.f < other.f

    # defining greater than for purposes of heap queue
    def __gt__(self, other):
      return self.f > other.f

def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Return reversed path

def make_level_map(x, y, blocked, additional_x = 0, additional_y = 0):
    map_plan = []
    for horizontal in range(x):
        plan_line = []

        for vertical in range(y):

            if (horizontal + additional_x, vertical + additional_y) in blocked:
                plan_line.append(1)
            else:
                plan_line.append(0)
        map_plan.append(plan_line)

    return map_plan

def map_hpa(maze_x, maze_y, split_size, blocked_area):
    x, y = int(maze_x / split_size), int(maze_y / split_size),
    divions = []
    for vertical in range(y):
        new_map = {}
        for horizontal in range(x):
            partition = []
            for additional_x in range(split_size):
                for additional_y in range(split_size):
                    partition.append(((horizontal * split_size) + additional_x, (vertical * split_size) + additional_y))

            new_map[(horizontal, vertical)] = partition

        divions.append(new_map)



    for vertical in divions:
        for sub_square_coordinate, real_nodes in vertical.items():
            neighbouring_cells = {'above': 0, 'below': 0, 'left': 0, 'right': 0}

            if sub_square_coordinate[0] == 0:
                neighbouring_cells['left'] = 1

            elif sub_square_coordinate[0] == x - 1:
                neighbouring_cells['right'] = 1

            if sub_square_coordinate[1] == 0:
                neighbouring_cells['above'] = 1

            elif sub_square_coordinate[1] == y - 1:
                neighbouring_cells['below'] = 1

            visualised_map = make_level_map(10, 10, blocked_area, additional_x = real_nodes[0][0], additional_y = real_nodes[0][1])
            print(real_nodes[0][0], real_nodes[0][1])
            print(sub_square_coordinate)
            print(neighbouring_cells)
            for line in visualised_map:
                print(line)
            print()


def astar(maze, start, end, allow_diagonal_movement = False):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    :param maze:
    :param start:
    :param end:
    :return:
    """

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Heapify the open_list and Add the start node
    heapq.heapify(open_list)
    heapq.heappush(open_list, start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = 1500 #(len(maze[0]) * len(maze) // 3)

    # what squares do we search
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
    if allow_diagonal_movement:
        adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1),)

    # Loop until you find the end
    while len(open_list) > 0:
        outer_iterations += 1

        if outer_iterations > max_iterations:
          # if we hit this point return the path such as it is
          # it will not contain the destination
          warn("giving up on pathfinding too many iterations")
          return return_path(current_node)

        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            return return_path(current_node)

        # Generate children
        children = []

        for new_position in adjacent_squares: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            # Child is on the closed list
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)

    warn("Couldn't get a path to destination")
    return None

