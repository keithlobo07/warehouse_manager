import time
import heapq

'''
search algorithm
•	Implement A* search algorithm
Implement heuristics:
Function to run A* and return:
•	path
•	cost
•	expansions
•	running time
'''

#print("search module loaded")

#manhattan distance heuristic (4 movement grid)
def manhattan (a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

#implement a* search algorithm
def a_star_search(grid, start, goal):
    start_time = time.time()

    width = len(grid[0])
    height = len(grid)

    #priority queue for open set
    open_set = []
    heapq.heappush(open_set, (0, 0, start))

    #for reconstructing path    
    came_from = {}
    
    
    #cost from start to this node
    g_cost = {start: 0}

    expansions = 0 #number of expanded nodes    

    #4 possible movements up, right, down, left
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  

    while open_set:
        f, g, current = heapq.heappop(open_set)
        expansions += 1
        
        #Goal reached
        if current == goal:
            break

        cx, cy = current

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy

            #check bounds
            if not (0 <= nx < width and 0 <= ny < height):
                continue

            #check obstacle
            if grid[ny][nx] == 1:
                continue

            new_cost = g_cost[current] + 1

            #if new node or found cheaper path, then update
            if (nx, ny) not in g_cost or new_cost < g_cost[(nx, ny)]:
                g_cost[(nx, ny)] = new_cost
                f_cost = new_cost + manhattan((nx, ny), goal)
                heapq.heappush(open_set, (f_cost, new_cost, (nx, ny)))
                came_from[(nx, ny)] = current

            
            
            
           
                 #path reconstruction
                 
  # If goal was never reached
    if goal not in came_from and start != goal:
        runtime = time.time() - start_time
        return None, float("inf"), expansions, runtime

    # Reconstruct path
    path = []
    node = goal

    # Special case: start == goal
    if start == goal:
        return [start], 0, expansions, time.time() - start_time

    while node != start:
        path.append(node)
        node = came_from[node]

    path.append(start)
    path.reverse()

    runtime = time.time() - start_time

    # cost is path length minus 1
    cost = len(path) - 1

    return path, cost, expansions, runtime           
            