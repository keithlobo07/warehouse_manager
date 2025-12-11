#dataSetGenerator.py
#Generates training data using A* search 

import random 
import sqlite3
import csv
import db_func
conn, cursor = db_func.db_connect()

from setGrid import generate_warehouse, get_warehouse_grid
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
    shelf_coords, path_coords = get_warehouse_grid()
    grid = generate_warehouse(Grid_Width, Grid_Height, shelf_coords)

    data = []

    s, a = get_warehouse_grid()

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