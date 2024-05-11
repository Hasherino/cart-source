from db_interface import get_map
from PIL import Image, ImageDraw
import math
from navigation import create_grid, a_star
from triangulation import triangulate_position

CELL_SIZE = 20
ARROW_LENGTH = 80
ARROW_WIDTH = 2
CART_LENGTH = 6
CART_WIDTH = 4
WALL_COLOR = (0, 0, 255)
LOCATION_COLOR = (0, 255, 0)
ARROW_COLOR = (0, 0, 0)
CART_CENTER_COLOR = (255, 0, 0)
CART_COLOR = 'yellow'
BACKGROUND_COLOR = 'gray'

path = None
heading = None

def generate_map(image_markers, cart_image_pos, orientation):
    global heading
    heading = orientation
    objects = get_map()

    max_x, max_y = 0, 0
    for obj in objects: 
        if obj[2] == 'DIMENSIONS':
            data = eval(obj[3])  
            max_x = data['width']  
            max_y = data['height'] 

    # Calculate canvas size
    canvas_width = max_x * CELL_SIZE
    canvas_height = max_y * CELL_SIZE

    # Create the map image
    map_img = Image.new('RGB', (canvas_width, canvas_height), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(map_img)

    virtual_map_markers = []
    for obj in objects:
        if obj[2] == 'WALL':
            data = eval(obj[3])
            start_x = data['startX'] * CELL_SIZE
            start_y = data['startY'] * CELL_SIZE
            end_x = data['endX'] * CELL_SIZE
            end_y = data['endY'] * CELL_SIZE
            if start_y == end_y:
                draw.line((start_x, start_y, end_x, end_y), fill=WALL_COLOR, width=CELL_SIZE)
            else:
                draw.rectangle((start_x, start_y, end_x, end_y), fill=WALL_COLOR)

        elif obj[2] == 'LOCATION':
            data = eval(obj[3])
            x = data['x'] * CELL_SIZE
            y = data['y'] * CELL_SIZE
            radius = CELL_SIZE // 3
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=LOCATION_COLOR)

        elif obj[2] == 'MARKER':
            data = eval(obj[3])
            letter = obj[1]
            virtual_map_markers.append((letter, data))

    path_x_a = 4 * CELL_SIZE
    path_x_b = 31 * CELL_SIZE
    path_y_a = 5 * CELL_SIZE
    path_y_b = 18 * CELL_SIZE
    # draw.rectangle((path_x_a, path_y_a, path_x_b, path_y_b), fill=None, outline=255)

    pos = triangulate_position(cart_image_pos, image_markers, virtual_map_markers)

    if pos is not None and heading is not None:
        cart_x = pos[0] * CELL_SIZE
        cart_y = pos[1] * CELL_SIZE
        adjusted_heading = 90 - heading

        arrow_end_x = cart_x + ARROW_LENGTH * math.cos(math.radians(adjusted_heading))
        arrow_end_y = cart_y - ARROW_LENGTH * math.sin(math.radians(adjusted_heading))

        # Calculate cart bounding box
        half_length = CART_LENGTH * CELL_SIZE / 2
        half_width = CART_WIDTH * CELL_SIZE / 2
        top_left = (-half_length, -half_width)
        top_right = (half_length, -half_width)
        bottom_right = (half_length, half_width)
        bottom_left = (-half_length, half_width)
        rotated_vertices = [
            rotate_point(top_left, adjusted_heading, (cart_x, cart_y)),
            rotate_point(top_right, adjusted_heading, (cart_x, cart_y)),
            rotate_point(bottom_right, adjusted_heading, (cart_x, cart_y)),
            rotate_point(bottom_left, adjusted_heading, (cart_x, cart_y))
        ]   

        draw.line((cart_x, cart_y, arrow_end_x, arrow_end_y), fill=ARROW_COLOR, width=ARROW_WIDTH)
        draw.polygon(rotated_vertices, fill=CART_COLOR)
        draw.ellipse((cart_x - radius, cart_y - radius, cart_x + radius, cart_y + radius), fill=CART_CENTER_COLOR)

        goal = None
        for obj in objects:
            if obj[2] == 'LOCATION' and obj[1] == 'milk':  # Find your milk
                data = eval(obj[3])
                goal = (data['x'], data['y'])
                break
        
        start = (int(cart_x // CELL_SIZE), int(cart_y // CELL_SIZE))
        if goal is not None:
            grid = create_grid(objects)
            try:
                path_c = a_star(grid, start, goal)

                if path_c:
                    for i in range(len(path_c) - 1):
                        x1, y1 = path_c[i][0] * CELL_SIZE, path_c[i][1] * CELL_SIZE
                        x2, y2 = path_c[i + 1][0] * CELL_SIZE, path_c[i + 1][1] * CELL_SIZE
                        draw.line((x1, y1, x2, y2), fill='blue', width=3)  # Example color

                global path
                path = path_c
            except Exception as e:
                print("A* failed", e)

    # Save the map image
    map_img.save('map.png')

def rotate_point(point, angle, center):
    angle_rad = math.radians(-angle)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    x, y = point
    x_new = x * cos_a - y * sin_a
    y_new = x * sin_a + y * cos_a
    return x_new + center[0], y_new + center[1]

def get_cart_heading():
    global heading
    return heading
