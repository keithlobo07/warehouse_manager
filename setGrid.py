#create a 2D grid (0 = empty, 1 = obstacle)
def create_grid(width, height):
    return [[0 for _ in range(width)] for _ in range(height)]

#Adding an obstacle at a specific grid cell
def add_obstacle(grid, x, y):
    grid[y][x]= 1 

def print_grid(grid):
    for row in grid:
        print(" ".join(str(cell) for cell in row))

w = 63
h = 13
grid = create_grid(w, h)

#goes through each row
for j in range(h):
    #goes through each column
    for i in range(w):
        if i % 2 == 1:
            grid[j][i] = 1

print("first loop worked yay")

#set rows 0, 6 and 12 back to 0
for a in range(h):
    if a == 0 or a == 6 or a == 12:
        #if at row 0 change all columns in row 0 back to 0/false
        for b in range(w):
            grid[a][b] = 0

print("second?")

print_grid(grid)

