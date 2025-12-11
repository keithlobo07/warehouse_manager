#simple grid implementation for dillon to start AI
import csv

#create a 2D grid (0 = empty, 1 = obstacle)
def create_grid(width, height):
    return [[0 for _ in range(width)] for _ in range(height)]

#Adding an obstacle at a specific grid cell
def add_obstacle(grid, x, y):
    grid[y][x]= 1 

#display grid as 0 and 1s
def print_grid(grid):
    for row in grid:
        print(" ".join(str(cell) for cell in row))

#save coords as array
def save_grid_as_array(grid):
    shelves = []

    for d in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[d][c] == 1:
                shelves.append([c,d])
    return shelves

#save array as csv
def save_grid_as_csv(shelves):
    with open("shelves.csv", "w", newline="") as file:
        writer = csv.writer(file)

        for x, y in shelves:
            writer.writerow([x,y])

w = 63
h = 13
grid = create_grid(w, h)

#goes through each row
for j in range(h):
    #goes through each column
    for i in range(w):
        if i % 2 == 1:
            add_obstacle(grid, i, j)

#set rows 0, 6 and 12 back to 0
for a in range(h):
    if a == 0 or a == 6 or a == 12:
        #if at row 0 change all columns in row 0 back to 0/false
        for b in range(w):
            grid[a][b] = 0

print_grid(grid)
print("\n")

s = save_grid_as_array(grid)
print(s)

save_grid_as_csv(s)
