import sqlite3
from db_func import *
from setGrid import *
from search import a_star_search

db_connect()
#view_tables()
print('---------------------WAREHOUSE MANAGER-----------------------\n')

print("Welcome to Warehouse Manager!\n")
print("1. Show warehouse grid\n2.Show robot initial state\n3.Run A* (with verbose mode)\n4.Show path + cost\n5.Show ML model predicting path cost\n6.Compare ML vs A*\n")
choice = int(input("Choose\n"))
while (choice != 0):
    print("1. Show warehouse grid\n2.Show robot initial state\n3.Run A* (with verbose mode)\n4.Show path + cost\n5.Show ML model predicting path cost\n6.Compare ML vs A*\n0.Exit")
    choice = int(input("Choose\n"))

    match choice:
        case 1:
            print("Show warehouse grid selected\n")
            #generate warehouse
            shelf_coords, path_coords = get_warehouse_grid()
            grid = generate_warehouse(63, 13, shelf_coords)
            #print warehouse grid
            print_grid(grid)
            #should print grid be a separate case?????????????           
        case 2:
            print("Show robot initial state selected\n")
            #explain robot rest point
            #show coords of robot and status
        case 3:
            print("Run A* (with verbose mode) selected\n")
            #run a_star_search
            #return path, cost, expansions, runtime
        case 4:
            print("Show path + cost selected\n")
            #can we use case 4 without case 3??????
        case 5:
            print("Show ML model predicting path cost selected\n")
            #
        case 6:
            print("Compare ML vs A* selected\n")
            #run both ml and a* and compare results
        case 0:
            print("EXITING\n")
            exit(0)
        case _:
            choice = int(input("Invalid. Please choose again"))

'''
•    Show warehouse grid
•    Show robot initial state
•    Run A* (with verbose mode)
•    Show path + cost
•    Show ML model predicting path cost
•    Compare ML vs A*
•    Mention running time
•    Explain results clearly
•    Clean screen layout
•    Trim video to 5 minutes
'''