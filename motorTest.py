import math

code = 1000

def calculate_rotation_angle(current_point, next_point, orientation):
  dx = next_point[0] - current_point[0]
  dy = next_point[1] - current_point[1]
  print(dx, dy)

  target_angle = -math.degrees(math.atan2(dy, dx))
  print(target_angle)

  target_angle = (target_angle + 360) % 360  
  orientation = (orientation + 360) % 360 

  angle_diff = target_angle - orientation
  if angle_diff > 180:
    angle_diff -= 360
  elif angle_diff < -180:
    angle_diff += 360

  return angle_diff  

def send_instructions(path):
    if path is None:
        print("No path found")
        return 0
    if len(path) == 3:
        return 1

    orientation = 10
    current_pos, next_pos = path[0], path[1]

    angle = calculate_rotation_angle(current_pos, next_pos, orientation)
    global code
    code = angle

    return 0

path = [(1, 12), (2, 11), (3, 10), (4, 9), (4, 8), (4, 7), (4, 6), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5), (13, 5), (14, 5)]
send_instructions(path)

print(code)