import math

def calculate_rotation_angle(current_point, next_point, orientation):
  dx = next_point[0] - current_point[0]
  dy = next_point[1] - current_point[1]

  target_angle = math.degrees(math.atan2(dy, dx)) + 90

  angle_diff = target_angle - orientation
  if angle_diff > 180:
    angle_diff -= 360
  elif angle_diff < -180:
    angle_diff += 360

  return angle_diff, target_angle

def send_instructions(path):
    global code
    if path is None:
        print("No path found")
        code = 1000
        return 0
    if len(path) <= 1:
        return 1

    orientation = 90
    current_pos, next_pos = path[0], path[1]

    if current_pos and next_pos and orientation is not None:
      angle, target_angle = calculate_rotation_angle(current_pos, next_pos, orientation)
      code = angle
    print("Current:", orientation)
    print("Target:", target_angle)
    print("Diff:", code)

    return 0

send_instructions([(15, 16), (14, 16), (15, 18)])