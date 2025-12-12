"""
---setGrid.py---\n
Simple warehouse grid generator for AI pathfinding (A*, ML)\n
Creates aisles and shelves and export shelf coordinates into shelves.csv
"""

# Imports
from db_func import db_connect

# Database connection
conn, cursor = db_connect()

def create_grid(width, height):
    """
    Creates a 2D grid initialized with zeros.
    0 indicates free space, and 1 indicates an obstacle.
    
    :param width: Width of the grid
    :param height: Height of the grid
    """
    return [[0 for _ in range(width)] for _ in range(height)]

def get_warehouse_grid():
    """
    Retrieves shelf and path coordinates from the database.
    """
    shelves=[]
    paths=[]
    cursor.execute("SELECT xPos, yPos FROM spaces WHERE type='shelf';")
    shelves = cursor.fetchall()
    cursor.execute("SELECT xPos, yPos FROM spaces WHERE type='path';")
    paths = cursor.fetchall()
    
    return shelves, paths

def add_obstacle(grid, x, y):
    """
    Adds an obstacle at the specified (x, y) position in the grid.
    
    :param grid: List of Lists representing the grid
    :param x: X-coordinate of the obstacle
    :param y: Y-coordinate of the obstacle
    """
    grid[y][x]= 1

def generate_warehouse(width, height, shelf_coords):
    """
    Generates a warehouse grid with shelves as obstacles.

    :param width: Width of the grid
    :param height: Height of the grid
    :param shelf_coords: List of tuples representing shelf coordinates
    """
    grid = create_grid(width, height)
    
    for x, y in shelf_coords:
        add_obstacle(grid, x, y)
    
    return grid

def print_grid(grid):
    """
    Displays the grid as 0s and 1s.
    
    :param grid: List of Lists representing the grid
    """
    for row in grid:
        print(" ".join(str(cell) for cell in row))

# test code
'''
shelf_coords, path_coords = get_warehouse_grid()
grid=generate_warehouse(63, 13, shelf_coords)

print_grid(grid)
'''