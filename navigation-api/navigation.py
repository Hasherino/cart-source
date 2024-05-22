import heapq
import numpy as np
import time

# Prefered path coordinates
path_x_a, path_y_a, path_x_b, path_y_b = 4, 5, 31, 18

def get_dimensions(objects):
    for obj in objects:
        if obj[2] == 'DIMENSIONS':
            return eval(obj[3])['width'], eval(obj[3])['height']
    return None, None

def create_grid(objects):
    width, height = get_dimensions(objects)
    grid = [[0 for _ in range(height + 1)] for _ in range(width + 1)]

    for obj in objects:
        if obj[1] == 'WALL':
            data = eval(obj[2])
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
        if elapsed > 1:
            print("Path finding algorithm timed out")
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
 
            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                if array[neighbor[0]][neighbor[1]] == -1:
                    gscore[neighbor] = gscore[neighbor] * 0.1
                    fscore[neighbor] = fscore[neighbor] * 0.1

                heapq.heappush(oheap, (fscore[neighbor], neighbor)) 
