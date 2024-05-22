import cv2
import numpy

def match_markers(image_markers, virtual_map_markers):
    matched_markers = []
    for image_marker in image_markers:
        for virtual_marker in virtual_map_markers:
            if image_marker['letter'] == virtual_marker[0]:
                matched_markers.append((image_marker, virtual_marker[1]))
                break
    return matched_markers

def triangulate_position(cart_image_pos, image_markers, virtual_map_markers):
    if image_markers is None or len(image_markers) < 3:
        return None

    matched_markers = match_markers(image_markers, virtual_map_markers)

    image_markers = [(m[0]['centerX'], m[0]['centerY']) for m in matched_markers]
    virtual_map_markers = [(m[1]['x'], m[1]['y']) for m in matched_markers] 

    transform_matrix = cv2.getPerspectiveTransform(
        src=numpy.float32(image_markers),
        dst=numpy.float32(virtual_map_markers)
    )

    image_pos_array = numpy.array([[cart_image_pos]], dtype='float32')
    virtual_pos_array = cv2.perspectiveTransform(image_pos_array, transform_matrix)

    virtual_x, virtual_y = virtual_pos_array[0][0]

    return virtual_x, virtual_y
