#setGrid.py 
#Simple warehouse grid generator for AI pathfinding (A*, ML)
#creates aisles and shelves and export shelf coordinates into shelves.csv

from db_func import db_connect

conn, cursor = db_connect()

# Create a empty 2D grid (0 = empty, 1 = obstacle)
def create_grid(width, height):
    return [[0 for _ in range(width)] for _ in range(height)]

# Get shelf and path coordinates from the database
def get_warehouse_grid():
    shelves=[]
    paths=[]
    cursor.execute("SELECT xPos, yPos FROM spaces WHERE type='shelf';")
    shelves = cursor.fetchall()
    cursor.execute("SELECT xPos, yPos FROM spaces WHERE type='path';")
    paths = cursor.fetchall()
    
    return shelves, paths

# Adding an obstacle at a specific grid cell
def add_obstacle(grid, x, y):
    grid[y][x]= 1

# Generate warehouse grid with given shelf coordinates
def generate_warehouse(width, height, shelf_coords):
    grid = create_grid(width, height)
    
    for x, y in shelf_coords:
        add_obstacle(grid, x, y)
    
    return grid

# Display grid as 0 and 1s
def print_grid(grid):
    for row in grid:
        print(" ".join(str(cell) for cell in row))

# what's going on here
'''
# Check if cell is free
def is_free(grid,x,y):
    return grid[x][y] == 0

# Set target position in the grid 
def set_target_position(grid, x, y):
    return (x, y)

# Gets robot position and target position
def get_robot_position(robot_pos):
    return robot_pos

def get_target_position(target_pos):
    return target_pos
'''
# test code
'''
shelf_coords, path_coords = get_warehouse_grid()
grid=generate_warehouse(63, 13, shelf_coords)

print_grid(grid)
'''