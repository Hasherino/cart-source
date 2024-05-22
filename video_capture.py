import numpy as np
import cv2
import requests
import pytesseract
from mss import mss
import json
import base64
import math

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\2269872\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
bounding_box = {'top': 100, 'left': 400, 'width': 1300, 'height': 900}
sct = mss()
markers = None

def GetBoundary(img):
    # --- Canny Edge Detection for Floor Boundary ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    canny_edges = cv2.Canny(blurred, 100, 200) 
    kernel = np.ones((3,3), np.uint8)  
    canny_edges = cv2.dilate(canny_edges, kernel, iterations=1)
    contours, _ = cv2.findContours(canny_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        floor_contour = max(contours, key=cv2.contourArea)
    else:
        return []

    floor_mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.drawContours(floor_mask, [floor_contour], -1, 255, cv2.FILLED)

    return floor_mask

def DetectCart(img):
    # --- Color Thresholding for cart's corners ---
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_purple = np.array([110, 50, 150])  
    upper_purple = np.array([180, 255, 255])  
    purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)
    purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # --- Color Thresholding for cart's front ---
    lower_cyan = np.array([50, 90, 150])
    upper_cyan = np.array([120, 255, 255])
    cyan_mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    cyan_contours, _ = cv2.findContours(cyan_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    all_points = []
    for cnt in purple_contours:
        if cv2.contourArea(cnt) > 10:
            points = cnt.squeeze()
            if points.ndim == 2 and points.shape[1] == 2:  
                all_points.extend(points) 

    if len(all_points) > 0:
        hull = cv2.convexHull(np.array(all_points))

        moments = cv2.moments(hull)
        center_x = int(moments["m10"] / moments["m00"])
        center_y = int(moments["m01"] / moments["m00"])
    else:
        center_x = None
        center_y = None

    closest_point = None
    if len(cyan_contours) and center_x and center_y > 0:
        cyan_contour = max(cyan_contours, key=cv2.contourArea)
        
        min_dist = float('inf')

        for pt in cyan_contour[:, 0, :]:
            x, y = pt 
            dist = np.sqrt((center_x - x)**2 + (center_y - y)**2)
            if dist < min_dist:
                min_dist = dist
                closest_point = (x, y)        

    return center_x, center_y, closest_point

def DetectMarkers(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 60, 80, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    filtered_contours = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        contour_overlaps = False
        for existing_cnt, _ in filtered_contours:
            existing_x, existing_y, existing_w, existing_h = cv2.boundingRect(existing_cnt)
            if x < existing_x + existing_w  and x + w > existing_x and \
            y < existing_y + existing_h and y + h > existing_y:
                contour_overlaps = True
                break
        
        if contour_overlaps:
            continue

        letter = within_area(cnt)
        if letter:
            filtered_contours.append((cnt, letter))
            cv2.rectangle(img,(x - 10,y - 10),(x+w + 10,y+h + 10),(0,255,0),2)

    # OCR and center calculation
    found_markers = []
    for cnt, letter in filtered_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # letter_image = img[y - 10:y+h + 10, x - 10:x+w + 10]
        # letter = pytesseract.image_to_string(letter_image, config='--psm 10')  # Single character mode

        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        found_markers.append({"letter": letter, "centerX": cX, "centerY": cY})

    global markers
    markers = found_markers
    print(markers)

def reasonable_size(w, h):
    min_area = 40  # Minimum expected area of a letter (adjust as needed)
    max_area = 170  # Maximum expected area of a letter (adjust as needed)
    return min_area <= w * h <= max_area

def reasonable_aspect_ratio(w, h):
    min_aspect = 0.7  # Minimum aspect ratio (width / height)
    max_aspect = 1.3  # Maximum aspect ratio 
    return min_aspect <= w / h <= max_aspect

def within_area(cnt):
    good_letters = [
        {'letter': 's', 'centerX': 200, 'centerY': 548}, 
        {'letter': 'o', 'centerX': 998, 'centerY': 282}, 
        {'letter': 'x', 'centerX': 1001, 'centerY': 566}, 
        {'letter': 'z', 'centerX': 200, 'centerY': 289}
    ] 

    selected_areas = []
    area_size = 100

    for letter_info in good_letters:
        x = letter_info['centerX']
        y = letter_info['centerY']
        letter = letter_info['letter']
        x_min = x - area_size // 2
        y_min = y - area_size // 2
        x_max = x + area_size // 2
        y_max = y + area_size // 2
        selected_areas.append((x_min, y_min, x_max, y_max, letter))

    M = cv2.moments(cnt)
    if M["m00"] == 0:
        return False
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])

    for area in selected_areas:
        x_min, y_min, x_max, y_max, letter = area
        if x_min <= cX <= x_max and y_min <= cY <= y_max:
            return letter
        
# Press q when you can see all markers in console, they will then be locked in
while True:
    sct_img = sct.grab(bounding_box)
    frame = np.array(sct_img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    floor_mask = GetBoundary(frame)
    frame[floor_mask == 0] = 0

    DetectMarkers(frame)
    cv2.imshow('screen', frame)

    if cv2.waitKey(40) == ord('q'):  # 40ms = 25 frames per second (1000ms/40ms) 
        break

def GetHeading(center, front):
    if center and front:
        delta_x = front[0] - center[0]
        delta_y = front[1] - center[1]
        heading = math.degrees(math.atan2(delta_y, delta_x))

        heading = (heading + 90) % 360
    else:
        return None

    return heading

while True:
    sct_img = sct.grab(bounding_box)
    frame = np.array(sct_img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    floor_mask = GetBoundary(frame)
    frame[floor_mask == 0] = 0

    center_x, center_y, closest_point = DetectCart(frame.copy())

    if closest_point is not None:
            cv2.arrowedLine(frame, (center_x, center_y), closest_point, (0, 255, 0), 2)
    
    _, imdata = cv2.imencode('.JPG', frame)
    encoded = base64.b64encode(imdata.tobytes()).decode('utf-8')
    heading = GetHeading((center_x, center_y), closest_point)

    request_data = {
        'image': encoded,
        'markers': markers,
        'cartX': center_x,
        'cartY': center_y,
        'cartHeading': heading
    }
    response = requests.put(
        'http://192.168.1.127:5001/upload', 
        data=json.dumps(request_data),
        headers={'Content-Type': 'application/json'}
    )
    cv2.imshow('screen', frame)

    if cv2.waitKey(40) == 27:  # 40ms = 25 frames per second (1000ms/40ms) 
        break

cv2.destroyAllWindows()
