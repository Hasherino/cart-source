import heapq
import numpy as np
import time

path_x_a, path_y_a, path_x_b, path_y_b = 4, 5, 31, 18

def get_dimensions(objects):
    for obj in objects:
        if obj[1] == 'DIMENSIONS':
            return eval(obj[2])['width'], eval(obj[2])['height']
    return None, None  # Handle the case where dimensions are not found

def create_grid(objects):
    width, height = get_dimensions(objects)
    grid = [[0 for _ in range(height + 1)] for _ in range(width + 1)]

    for obj in objects:
        if obj[0] == 'WALL':
            data = eval(obj[1])
            sx, sy, ex, ey = data['startX'], data['startY'], data['endX'], data['endY']
            for x in range(sx, ex + 1):
                for y in range(sy, ey + 1):
                    grid[x][y] = 1

    for x in range(path_x_a, path_x_b + 1):
        for y in range(path_y_a, path_y_b + 1):
            if not (path_y_a < y < path_y_b) or x == 4 or x == 31:
                grid[x][y] = -1

    return np.squeeze(np.asarray(grid))

def heuristic(a, b):
    return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def a_star(array, start, goal):
    neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]

    close_set = set()
    came_from = {}

    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}

    oheap = []
    heapq.heappush(oheap, (fscore[start], start))

    start_time = time.time()
 
    while oheap:
        end_time = time.time()
        elapsed = end_time - start_time
        if elapsed > 2:
            print("A* timed out")
            return None

        current = heapq.heappop(oheap)[1]
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            data = data + [start]
            data = data[::-1]
            return data

        close_set.add(current)

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j            
            tentative_g_score = gscore[current] + heuristic(current, neighbor)

            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:                
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    continue
            else:
                continue
 
            if neighbor in close_set:
                continue
 
            if  tentative_g_score <= gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                if array[neighbor[0]][neighbor[1]] == -1:
                    gscore[neighbor] = gscore[neighbor] * 0.1
                    fscore[neighbor] = fscore[neighbor] * 0.1

                heapq.heappush(oheap, (fscore[neighbor], neighbor)) 

objects = [ ('floor', 'DIMENSIONS', '{ "width": 35, "height": 23 }'),
    ('bottom wall', 'WALL', '{ "startX": 9, "endX": 25, "startY": 0, "endY": 0 }'),
    ('middle wall', 'WALL', '{ "startX": 9, "endX": 25, "startY": 11, "endY": 12 }'),
    ('top wall', 'WALL', '{ "startX": 9, "endX": 25, "startY": 23, "endY": 23 }'),
    ('z', 'MARKER', '{ "x": 4, "y": 5 }'),
    ('o', 'MARKER', '{ "x": 31, "y": 5 }'),
    ('s', 'MARKER', '{ "x": 4, "y": 18 }'),
    ('x', 'MARKER', '{ "x": 31, "y": 18 }'),
    ('milk', 'LOCATION', '{ "x": 14, "y": 5 }')]

goal = None
for obj in objects:
    if obj[1] == 'LOCATION' and obj[0] == 'milk':  # Find your milk
        data = eval(obj[2])
        goal = (data['x'], data['y'])
        break

start = (1, 12)
if goal is not None:
    grid = create_grid(objects)
    try:
        path_c = a_star(grid, start, goal)
    except Exception as e:
        print("A* failed", e)

print(path_c)