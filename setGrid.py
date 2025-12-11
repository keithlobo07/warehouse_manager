#setGrid.py 
#Simple warehouse grid generator for AI pathfinding (A*, ML)
#creates aisles and shelves and export shelf coordinates into shelves.csv

import csv

#create a empty 2D grid (0 = empty, 1 = obstacle)
def create_grid(width, height):
    return [[0 for _ in range(width)] for _ in range(height)]

#Adding an obstacle at a specific grid cell
def add_obstacle(grid, x, y):
    grid[y][x]= 1 


#display grid as 0 and 1s
def print_grid(grid):
    for row in grid:
        print(" ".join(str(cell) for cell in row))

#Save coordinates of all shelves into an array
def save_shelves_as_array(grid):
    shelves = []

    for d in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[d][c] == 1:
                shelves.append([c,d])
    return shelves

#Save shelves array as CSV file 
def save_shelves_as_csv(shelves):
    with open("shelves.csv", "w", newline="") as file:
        writer = csv.writer(file)
        
        for x, y in shelves:
            writer.writerow([x,y])

#Save coordinates of all aisles into an array
def save_aisles_as_array(grid):
    aisles = []

    for d in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[d][c] == 0:
                aisles.append([c,d])
    return aisles

#Save aisles array as CSV file 
def save_aisles_as_csv(aisles):
    with open("aisles.csv","w", newline="") as file:
        writer = csv.writer(file)

        for x,y in aisles:
            writer.writerow([x,y])

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

#Warehouse Setup
def generate_warehouse(w=63, h=13, a1=0, a2=6,a3=12):
    grid = create_grid(w, h)

    # Fill every odd column with shelves
    for j in range(h):
        for i in range(w):
            if i % 2 == 1:
                add_obstacle(grid, i, j)

    # Set aisles
    for a in range(h):
        if a in (a1, a2, a3):
            for b in range(w):
                grid[a][b] = 0

    return grid

# Run only when executed directly
if __name__ == "__main__":
    grid = generate_warehouse()
    
    # Print the generated grid
    print_grid(grid)
    print("\n")

    # Save shelves
    s = save_shelves_as_array(grid)
    print(s)  # Remove this after testing

    save_shelves_as_csv(s)
    print("shelves.csv file created successfully.")

    # Save aisles
    a = save_aisles_as_array(grid)
    print(a)  # Remove this after testing

    save_aisles_as_csv(a)
    print("aisles.csv file created successfully.")
