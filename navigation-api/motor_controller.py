from virtual_map import get_cart_info
import math

code = 1000

def calculate_rotation_angle(current_point, next_point, orientation):
  dx = next_point[1] - current_point[1]
  dy = next_point[0] - current_point[0]

  target_angle = math.degrees(math.atan2(dy, dx))

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
    if len(path) == 1:
        return 1

    _, _, orientation = get_cart_info()
    current_pos, next_pos = path[0], path[1]

    angle = calculate_rotation_angle(current_pos, next_pos, orientation)
    global code
    code = angle

    return 0

def stop():
   global code
   code = 1000
