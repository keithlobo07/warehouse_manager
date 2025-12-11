#dataSetGenerator.py
#Generates training data using A* search 

import csv
import random 

from setGrid import generate_warehouse
from search import a_star_search

#data needed: start_x, start_y, goal_x, goal_y, path_length, path_exists
'''
variable:   data type,  limits, desc
start_x:    int,        0-62    start x coord
start_y:    int,        0-12    start y coord
goal_x:     int,        0-62    end x coord
goal_y:     int,        0-12    end y coord
path_length:int,                number of nodes - 1
path_exists:int,        0/1     f/t whether path exists
'''
#settting up grid parameters
Grid_Width = 63
Grid_Height = 13    
Train_samples =  500
Test_samples =  100

#random coord helpers
def random_x():
    return random.randint(0, Grid_Width - 1)    

def random_y(): 
    return random.randint(0, Grid_Height - 1)   

#load shelf coords
def load_shelf_coordinates(filename="shelves.csv"):
    shelves = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            x, y = map(int, row)
            shelves.append((x, y))
    return shelves

#load aisle coords
def load_aisle_coordinates(filename="aisles.csv"):
    aisles = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            x, y = map(int, row)
            aisles.append((x, y))
    return aisles

#Creates one training data sample   
def generate_sample(grid, aisles, shelves):
    start = (random.choice(aisles))
    goal = (random.choice(shelves))
    
    path, cost, expansions, run_time = a_star_search(grid, start, goal)

    #If no path exists 
    if path is None:
        return [
            start[0], start[1],
            goal[0], goal[1],
            -1,     #path length
            0       #path exists (false)
        ]


    return[
     start[0], start[1],
        goal[0], goal[1],
        cost,   #path length
        1       #path exists (true)
    ]



#Generate Dataset
def generate_dataset(filename, num_samples):
    grid = generate_warehouse(Grid_Width, Grid_Height)

    data = []

    s = load_shelf_coordinates("shelves.csv")
    a = load_aisle_coordinates("aisles.csv")

    for _ in range(num_samples):
            sample = generate_sample(grid, a, s)
            data.append(sample)

    #save to csv
    with open(filename,'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['start_x', 'start_y', 'goal_x', 'goal_y', 'path_length', 'path_exists'])
        writer.writerows(data)

    print(f"Dataset '{filename}' with {num_samples} samples generated.")


#Main execution
if __name__ == "__main__":
     
     #training data - 500 smaples 
     generate_dataset('training_data.csv', Train_samples)

     #test data - 100 smaples(diffrent from training data)
     generate_dataset('test_data.csv', Test_samples)

#data returned: path, cost, expansions, running time


'''
def checkPath(path, path_exists, path_length):
    if path is None: 
        path_exists = 0 
        path_length = -1 
    else: 
        path_exist = 1 
        path_length = len(path)
'''
#TEST 1 go from (0, 0) to (0, 40)
#start_x1 = 0
#start_y1 = 0
#goal_x1 = 0
#goal_y1 = 40
#exp_path_length1 = 40
#exp_path_exists1 = 1

#TEST 2 go from (2,1) to (8,1)
#start_x2 = 2
#start_y2 = 1
#goal_x2 = 8
#goal_y2 = 1
#exp_path_length2 = 8
#exp_path_exists2 = 1

#TEST 3
#start_x3 = ranWidth()
#start_y3 = ranHeight()
#goal_x3 = ranWidth()
#goal_y3 = ranHeight()
#exp_path_length3 = -1
#exp_path_exists3 = -1

#TEST 4
#start_x4 = ranWidth()
#start_y4 = ranHeight()
#goal_x4 = ranWidth()
#goal_y4 = ranHeight()
#exp_path_length4 = -1
#exp_path_exists4 = -1

#TEST 5
#start_x5 = ranWidth()
#start_y5 = ranHeight()
#goal_x5 = ranWidth()
#goal_y5 = ranHeight()
#exp_path_length5 = -1
#exp_path_exists5 = -1

#TEST 6
#start_x6 = ranWidth()
#start_y6 = ranHeight()
#goal_x6 = ranWidth()
#goal_y6 = ranHeight()
#exp_path_length6 = -1
#exp_path_exists6 = -1

#TEST 7
#start_x7 = ranWidth()
#start_y7 = ranHeight()
#goal_x7 = ranWidth()
#goal_y7 = ranHeight()
#exp_path_length7 = -1
#exp_path_exists7 = -1

#TEST 8
#start_x8 = ranWidth()
#start_y8 = ranHeight()
#goal_x8 = ranWidth()
#goal_y8 = ranHeight()
#exp_path_length8 = -1
#exp_path_exists8 = -1
