#simple grid implementation for dillon to start AI

#create a 2D grid (0 = empty, 1 = obstacle)
def create_grid(width, height):
    return [[0 for _ in range(width)] for _ in range(height)]

#Adding an obstacle at a specific grid cell
def add_obstacle(grid, x, y):
    grid[y][x]= 1 

#check if cell is free
def is_free(grid,x,y):
    return grid[x][y] == 0

#Set target position in the grid 
def set_target_position(grid, x, y):
    return (x, y)

# Gets robot position and target position
def get_robot_position(robot_pos):
    return robot_pos

def get_target_position(target_pos):
    return target_pos