#setGrid.py 
#Simple warehouse grid generator for AI pathfinding (A*, ML)
#creates ailes and shelves and export shelf coordinates into shelves.csv

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
def save_grid_as_array(grid):
    shelves = []

    for d in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[d][c] == 1:
                shelves.append([c,d])
    return shelves

#Save shelves array as CSV file 
def save_grid_as_csv(shelves):
    with open("shelves.csv", "w", newline="") as file:
        writer = csv.writer(file)
        
        for x, y in shelves:
            writer.writerow([x,y])


#Warehouse Setup


def generate_warehouse(w=63, h=13):
    grid = create_grid(w, h)

    # Fill every odd column with shelves
    for j in range(h):
        for i in range(w):
            if i % 2 == 1:
                add_obstacle(grid, i, j)

    # Set aisles
    for a in range(h):
        if a in (0, 6, 12):
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
    s = save_grid_as_array(grid)
    print(s)  # Remove this after testing

    save_grid_as_csv(s)
    print("shelves.csv file created successfully.")
