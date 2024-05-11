from virtual_map import get_cart_heading
import math

code = 1000

def calculate_rotation_angle(current_point, next_point, orientation):
  dx = next_point[0] - current_point[0]
  dy = next_point[1] - current_point[1]

  target_angle = -math.degrees(math.atan2(dy, dx))

  target_angle = (target_angle + 360) % 360  
  orientation = (orientation + 360) % 360 

  angle_diff = target_angle - orientation
  if angle_diff > 180:
    angle_diff -= 360
  elif angle_diff < -180:
    angle_diff += 360

  return angle_diff  

def send_instructions(path):
    global code
    if path is None:
        print("No path found")
        code = 1000
        return 0
    if len(path) == 3:
        return 1

    orientation = get_cart_heading()
    current_pos, next_pos = path[0], path[1]

    if current_pos and next_pos and orientation:
      angle = calculate_rotation_angle(current_pos, next_pos, orientation)
      code = angle
    print("angle", code)

    return 0

def stop():
   global code
   code = 1000
