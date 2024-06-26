import cv2
import math
import numpy as np
from enum import Enum
from itertools import product
from src.image_process.image_vehicle import VehicleImage
from src.image_process.consts import *


class BoardOrientation(Enum):
    DOWN = 0
    RIGHT = 1
    UP = 2
    LEFT = 3


class VehicleOrientation(Enum):
    VERTICAL = 0
    HORIZONTAL = 1


class BoardImage:
    image: np.ndarray
    board_orientation: BoardOrientation
    board_matrix: np.ndarray

    def __init__(self, image_path: str):
        self.image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2HSV)
        self.board_orientation = BoardOrientation.DOWN
        self.board_matrix = np.zeros((6, 6), dtype=int)

    def process(self, vehicles: list[VehicleImage]):
        board_corners = BoardImage.find_board_corners(self.image)
        self.image = BoardImage.perspective_transform(self.image, board_corners)
        self.board_orientation = BoardImage.find_board_orientation(self.image)
        self.image = BoardImage.remove_board_edges(self.image, self.board_orientation)
        self.find_vehicles(vehicles)
        self.board_matrix = np.rot90(self.board_matrix, k=self.board_orientation.value)
        return self.board_matrix

    @staticmethod
    def sort_points_clockwise(points: np.ndarray) -> np.ndarray:
        # Calculate the centroid of the points
        cx = sum(pt[0] for pt in points) / len(points)
        cy = sum(pt[1] for pt in points) / len(points)
        centroid = (cx, cy)

        # Calculate the angle of each point with respect to the centroid
        angles = []
        for pt in points:
            dx = pt[0] - centroid[0]
            dy = pt[1] - centroid[1]
            angle = (math.atan2(dy, dx) + 2 * math.pi) % (2 * math.pi)
            angles.append(angle)

        # Sort the points by angle in clockwise order
        sorted_points = [pt for _, pt in sorted(zip(angles, points))]

        # Find the top left corner
        xSorted = points[np.argsort(points[:, 0]), :]
        leftMost = xSorted[:2, :]
        top_left = leftMost[np.argsort(leftMost[:, 1]), :][0]

        # Make the top left corner the first point
        while not (sorted_points[0] == top_left).all():
            sorted_points.insert(0, sorted_points.pop())

        return np.array(sorted_points, dtype="float32")

    @staticmethod
    def perspective_transform(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
        # obtain a consistent order of the points and unpack
        rect = BoardImage.sort_points_clockwise(corners)
        (tl, tr, br, bl) = rect

        # maximum width
        width_top = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_bottom = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        w = max(width_top, width_bottom)

        # maximum height
        height_right = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_left = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        h = max(height_right, height_left)

        # aspect ratio in the image
        ar_vis = float(w) / float(h)
        # center point of the image
        u0 = (image.shape[1]) / 2.0
        v0 = (image.shape[0]) / 2.0

        # convert to homogeneous coordinates
        m1 = np.array((tl[0], tl[1], 1)).astype('float32')
        m2 = np.array((tr[0], tr[1], 1)).astype('float32')
        m3 = np.array((bl[0], bl[1], 1)).astype('float32')
        m4 = np.array((br[0], br[1], 1)).astype('float32')

        # calculate the focal distance, stages 11 and 12
        k2 = np.dot(np.cross(m1, m4), m3) / np.dot(np.cross(m2, m4), m3)
        k3 = np.dot(np.cross(m1, m4), m2) / np.dot(np.cross(m3, m4), m2)

        n2 = k2 * m2 - m1
        n3 = k3 * m3 - m1

        n21 = n2[0]
        n22 = n2[1]
        n23 = n2[2]

        n31 = n3[0]
        n32 = n3[1]
        n33 = n3[2]

        # Calculate the focal length stage 21
        f = math.sqrt(np.abs((1.0 / (n23 * n33)) * ((n21 * n31 - (n21 * n33 + n23 * n31) * u0 + n23 * n33 * u0 ** 2) + (
                    n22 * n32 - (n22 * n33 + n23 * n32) * v0 + n23 * n33 * v0 ** 2))))

        # Calibration matrix
        A = np.array([[f, 0, u0], [0, f, v0], [0, 0, 1]]).astype('float32')
        At = np.transpose(A)
        Ati = np.linalg.inv(At)
        Ai = np.linalg.inv(A)

        # calculate the real aspect ratio, stage 20
        ar_real = math.sqrt(np.dot(np.dot(np.dot(n2, Ati), Ai), n2) / np.dot(np.dot(np.dot(n3, Ati), Ai), n3))

        # Rectification section 3.3
        if ar_real < ar_vis:
            W = int(w)
            H = int(W / ar_real)
        else:
            H = int(h)
            W = int(ar_real * H)

        # Apply the perspective transform
        points = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
        M = cv2.getPerspectiveTransform(rect, points)
        return cv2.warpPerspective(image, M, (W, H))

    @staticmethod
    def find_board_corners(image: np.ndarray) -> np.ndarray:
        m, n = image.shape[0:2]
        mask = cv2.inRange(image, *BOARD_COLOR_RANGE)
        ret, threshold = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        edges = cv2.Canny(threshold, CORNERS_CANNY_THRESHOLD1, CORNERS_CANNY_THRESHOLD2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, CORNERS_MORPH_RECT_DIMENSIONS)
        edges = cv2.dilate(edges, kernel, iterations=CORNERS_MORPH_ITERATIONS)
        # Hough lines
        lines_image = edges.copy()
        lines = cv2.HoughLinesP(
            edges,  # Input edge image
            2,  # Distance resolution in pixels
            np.pi / 180,  # Angle resolution in radians
            threshold=300,  # Min number of votes for valid line
            minLineLength=max(m, n) * CORNERS_LINES_MIN_LENGTH,
            maxLineGap=max(m, n) * CORNERS_LINES_MAX_GAP
        )
        # Iterate over points
        epsilon = 0.000001
        for line1_index, line1 in enumerate(lines):
            # Extracted points nested in the list
            line1_x1, line1_y1, line1_x2, line1_y2 = line1[0]
            m1 = (line1_y2 - line1_y1) / (line1_x2 - line1_x1) if np.abs(line1_x2 - line1_x1) > epsilon else np.inf
            for line2 in lines[line1_index + 1:]:
                # Extracted points nested in the list
                line2_x1, line2_y1, line2_x2, line2_y2 = line2[0]
                m2 = (line2_y2 - line2_y1) / (line2_x2 - line2_x1) if np.abs(line2_x2 - line2_x1) > epsilon else np.inf
                if np.abs(m1) < epsilon or np.abs(m2) < epsilon:
                    if np.abs(m1) < epsilon and np.abs(m2) < epsilon:
                        dist = np.abs(line1_y1 - line2_y1)
                    else:
                        continue
                elif m1 == np.inf and m2 == np.inf:
                    dist = np.abs(line1_x1 - line2_x1)
                elif np.abs(m1 - m2) <= CORNERS_LINES_SLOPE_THRESHOLD and (m2 + 1 / m1) != 0:
                    x_cross = (line1_y1 + line1_x1 / m1 - line2_y1 + m2 * line2_x1) / (m2 + 1 / m1)
                    y_cross = line2_y1 + m2 * (x_cross - line2_x1)
                    dist = np.sqrt((line1_x1 - x_cross) ** 2 + (line1_y1 - y_cross) ** 2)
                else:
                    continue
                if dist > CORNERS_LINES_DISTANCE_THRESHOLD * m:
                    # Draw the lines joing the points
                    # On the original image
                    cv2.line(lines_image, (line1_x1, line1_y1), (line1_x2, line1_y2), (255, 255, 255), 1)
                    cv2.line(lines_image, (line2_x1, line2_y1), (line2_x2, line2_y2), (255, 255, 255), 1)

        closing = cv2.morphologyEx(lines_image, cv2.MORPH_CLOSE, kernel, iterations=CORNERS_MORPH_ITERATIONS)
        contours = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        contour = sorted(contours, key=cv2.contourArea, reverse=True)[0]

        length = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, CORNERS_APPROX_POLY_DP * length, True)
        # Get the convex hull for the target contour:
        hull = cv2.convexHull(approx)
        # Create image for good features to track:
        # Black image same size as original input
        hullImg = np.zeros((m, n), dtype=np.uint8)
        # Draw the points:
        cv2.drawContours(hullImg, [hull], 0, 255, 5)
        maxCorners = 4
        qualityLevel = 0.01
        minDistance = int(max(m, n) / maxCorners)
        # Get the corners:
        corners = cv2.goodFeaturesToTrack(hullImg, maxCorners, qualityLevel, minDistance)
        corners = np.intp(corners)
        return corners.sum(axis=1)

    @staticmethod
    def find_board_orientation(image: np.ndarray) -> BoardOrientation:
        logo_color_lower = (90, 10, 120)
        logo_color_upper = (110, 50, 210)

        m, n = image.shape[0:2]
        logo_area_threshold = ((m / 6) * 0.6) * ((n / 6) * 0.6)

        # Find border
        mask = cv2.inRange(image, (30, 0, 20), (120, 120, 120))
        ret, threshold = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 5))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 9))
        dilate = cv2.dilate(threshold, horizontal_kernel, iterations=2)
        dilate = cv2.dilate(dilate, vertical_kernel, iterations=3)
        closing = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, horizontal_kernel, iterations=12)
        closing = cv2.morphologyEx(closing, cv2.MORPH_CLOSE, vertical_kernel, iterations=12)
        masked_closing_color = cv2.bitwise_and(image, image, mask=closing)

        # Logo search
        mask_logo = cv2.inRange(masked_closing_color, logo_color_lower, logo_color_upper)
        ret, threshold = cv2.threshold(mask_logo, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilate_logo = cv2.dilate(threshold, kernel, iterations=5)
        closing_logo = cv2.morphologyEx(dilate_logo, cv2.MORPH_CLOSE, kernel, iterations=5)

        contours = cv2.findContours(closing_logo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours[0]:
            contours = contours[0] if len(contours) == 2 else contours[0]
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            for contour in contours:
                (x, y, w, h) = cv2.boundingRect(contour)
                if w * h > logo_area_threshold and max(w, h) / min(w, h) < 3:
                    if h >= m * 0.9:
                        return BoardOrientation.DOWN
                    elif y <= m * 0.1:
                        return BoardOrientation.UP
                    elif x <= n * 0.1:
                        return BoardOrientation.RIGHT
                    elif x + w >= n * 0.9:
                        return BoardOrientation.LEFT
                    else:
                        continue
                    break
        # We failed to understand the orientation from the logo, fallback to default
        return BoardOrientation.DOWN

    @staticmethod
    def remove_board_edges(image: np.ndarray, orientation: BoardOrientation) -> np.ndarray:
        m, n = image.shape[0:2]
        if orientation == BoardOrientation.DOWN:
            return image[round(m * 0.08):round(-m * 0.14), round(n * 0.06):round(-n * 0.06)]
        elif orientation == BoardOrientation.RIGHT:
            return image[round(m * 0.06):round(-m * 0.06), round(n * 0.14):round(-n * 0.08)]
        elif orientation == BoardOrientation.UP:
            return image[round(m * 0.14):round(-m * 0.09), round(n * 0.06):round(-n * 0.06)]
        elif orientation == BoardOrientation.LEFT:
            return image[round(m * 0.06):round(-m * 0.06), round(n * 0.08):round(-n * 0.14)]

    def add_vehicle_to_board(self, vehicle, row, col, vehicle_orientation):
        if vehicle_orientation == VehicleOrientation.HORIZONTAL:
            self.board_matrix[row:row + 1, col:col + vehicle.size] = vehicle.id
        else:
            self.board_matrix[row - vehicle.size + 1:row + 1, col:col + 1] = vehicle.id

    def is_in_range(self, vehicle, row, col, vehicle_orientation):
        if vehicle_orientation == VehicleOrientation.HORIZONTAL:
            return 0 <= row < self.board_matrix.shape[0] \
                and col >= 0 and (col + vehicle.size - 1) < self.board_matrix.shape[1]
        else:
            return (row - vehicle.size + 1) >= 0 and row < self.board_matrix.shape[0] \
                and 0 <= col < self.board_matrix.shape[1]

    def is_available(self, vehicle, row, col, vehicle_orientation):
        if self.is_in_range(vehicle, row, col, vehicle_orientation):
            if vehicle_orientation == VehicleOrientation.HORIZONTAL:
                return not self.board_matrix[row:row + 1, col:col + vehicle.size].any()
            else:
                return not self.board_matrix[row - vehicle.size + 1:row + 1, col:col + 1].any()
        return False

    def find_vehicles(self, vehicles, orientation_ratio_threshold=1.2, location_threshold=0.35):

        self.board_matrix = np.zeros((6, 6), dtype=int)
        m, n = self.image.shape[0:2]

        def filter_by_red_car(optional_locations):
            # find row and col according to board orientation
            updated_optional_locations = []
            for optional_location in optional_locations:
                row, col, vehicle_orientation = optional_location

                if ((self.board_orientation == BoardOrientation.DOWN and row == 2 and
                     vehicle_orientation == VehicleOrientation.HORIZONTAL) or
                        (self.board_orientation == BoardOrientation.RIGHT and col == 3 and
                         vehicle_orientation == VehicleOrientation.VERTICAL) or
                        (self.board_orientation == BoardOrientation.UP and row == 3 and
                         vehicle_orientation == VehicleOrientation.HORIZONTAL) or
                        (self.board_orientation == BoardOrientation.LEFT and col == 2 and
                         vehicle_orientation == VehicleOrientation.VERTICAL)):
                    updated_optional_locations.append(optional_location)

            if not updated_optional_locations:
                return optional_locations

            return updated_optional_locations

        def filter_by_edges(vehicles_to_process, vehicles_to_optional_locations, threshold=0.03):
            new_vehicle_to_optional_locations = {}
            for vehicle, optional_locations in vehicles_to_optional_locations.items():
                (x, y, w, h) = vehicles_to_process[vehicle]
                is_near_right_edge = x + w >= n - (n * threshold)
                is_near_top_edge = y <= m * threshold
                new_optional_locations = []
                for optional_location in optional_locations:
                    row, col, vehicle_orientation = optional_location
                    if is_near_right_edge:
                        size = vehicle.size if vehicle_orientation == VehicleOrientation.HORIZONTAL else 1
                        if col + size - 1 == 5:
                            new_optional_locations.append(optional_location)
                    elif is_near_top_edge:
                        size = 1 if vehicle_orientation == VehicleOrientation.HORIZONTAL else vehicle.size
                        if row - size + 1 == 0:
                            new_optional_locations.append(optional_location)
                    else:
                        new_optional_locations.append(optional_location)
                if new_optional_locations:
                    new_vehicle_to_optional_locations[vehicle] = new_optional_locations
                else:
                    new_vehicle_to_optional_locations[vehicle] = optional_locations
            return new_vehicle_to_optional_locations

        def filter_by_conflicts(vehicles_to_optional_locations):
            previous_len = len(vehicles_to_optional_locations) + 1
            while previous_len != len(vehicles_to_optional_locations):
                previous_len = len(vehicles_to_optional_locations)
                new_vehicle_to_optional_locations = {}
                for vehicle, optional_locations in vehicles_to_optional_locations.items():
                    new_optional_locations = []
                    for optional_location in optional_locations:
                        row, col, vehicle_orientation = optional_location
                        if self.is_available(vehicle, row, col, vehicle_orientation):
                            new_optional_locations.append(optional_location)
                    if len(new_optional_locations) == 1:
                        row, col, vehicle_orientation = new_optional_locations[0]
                        self.add_vehicle_to_board(vehicle, row, col, vehicle_orientation)
                    if len(new_optional_locations) > 1:
                        new_vehicle_to_optional_locations[vehicle] = new_optional_locations
                vehicles_to_optional_locations = new_vehicle_to_optional_locations
            return vehicles_to_optional_locations

        vehicle_process_col_location = {}
        vehicle_process_row_location = {}
        vehicle_process_orientation = {}

        for vehicle in vehicles:
            vehicle_location = vehicle.find_vehicle(self.image, ((m/6)*0.6) * ((n/6)*0.6))
            if not vehicle_location:
                continue
            (x, y, w, h) = vehicle_location
            vehicle_orientation = VehicleOrientation.HORIZONTAL if w > h else VehicleOrientation.VERTICAL
            row = round((y + h) / (m / 6) - 1)
            col = round(x / (n / 6))
            size = vehicle.size
            further_process = False

            if max(w, h) / min(w, h) < orientation_ratio_threshold:
                vehicle_process_orientation[vehicle] = (x, y, w, h)
                further_process = True
            if np.abs(row - ((y + h) / (m / 6) - 1)) > location_threshold:
                vehicle_process_row_location[vehicle] = (x, y, w, h)
                further_process = True
            if np.abs(col - x / (n / 6)) > location_threshold:
                vehicle_process_col_location[vehicle] = (x, y, w, h)
                further_process = True

            if not further_process:
                if vehicle_orientation == VehicleOrientation.HORIZONTAL:
                    col = min(6 - size, col)
                else:
                    row = max(size - 1, row)

                if self.is_available(vehicle, row, col, vehicle_orientation):
                    self.add_vehicle_to_board(vehicle, row, col, vehicle_orientation)
                else:
                    # vehicle_process_orientation[vehicle] = (x, y, w, h)
                    vehicle_process_row_location[vehicle] = (x, y, w, h)
                    vehicle_process_col_location[vehicle] = (x, y, w, h)

        vehicles_to_process = vehicle_process_row_location | vehicle_process_col_location | vehicle_process_orientation
        vehicles_to_optional_locations = {}

        for vehicle, (x, y, w, h) in vehicles_to_process.items():
            vehicle_orientations = [VehicleOrientation.HORIZONTAL if w > h else VehicleOrientation.VERTICAL]
            rows = [round((y + h) / (m / 6) - 1)]
            cols = [round(x / (n / 6))]
            if vehicle in vehicle_process_row_location:
                if (y + h) / (m / 6) - 1 > rows[0]:  # round down
                    rows.append(rows[0] + 1)
                else:
                    rows.append(rows[0] - 1)
            if vehicle in vehicle_process_col_location:
                if x / (n / 6) > cols[0]:  # round down
                    cols.append(cols[0] + 1)
                else:
                    cols.append(cols[0] - 1)
            if vehicle in vehicle_process_orientation:
                vehicle_orientations.append(VehicleOrientation.VERTICAL if
                                            vehicle_orientations[0] == VehicleOrientation.HORIZONTAL
                                            else VehicleOrientation.HORIZONTAL)
                # Add options by top right corner, order by likely orientation
                if vehicle_orientations[0] == VehicleOrientation.HORIZONTAL:
                    rows.append(round(y / (m / 6)))
                    rows.append(round(y / (m / 6) + vehicle.size - 1))
                    cols.append(round((x + w) / (n / 6) - vehicle.size))
                    cols.append(round((x + w) / (n / 6) - 1))
                else:
                    rows.append(round(y / (m / 6) + vehicle.size - 1))
                    rows.append(round(y / (m / 6)))
                    cols.append(round((x + w) / (n / 6) - 1))
                    cols.append(round((x + w) / (n / 6) - vehicle.size))

            # remove duplicates in list while preserving the order with list(dict.fromkeys())
            vehicles_to_optional_locations[vehicle] = list(
                product(list(dict.fromkeys(rows)), list(dict.fromkeys(cols)), vehicle_orientations))

        # prevent board out of bounds
        for vehicle, optional_locations in vehicles_to_optional_locations.items():
            new_optional_locations = []
            for optional_location in optional_locations:
                row, col, vehicle_orientation = optional_location
                if self.is_in_range(vehicle, row, col, vehicle_orientation):
                    new_optional_locations.append(optional_location)
                    continue
                else:
                    if vehicle_orientation == VehicleOrientation.HORIZONTAL:
                        new_optional_locations.append((row, min(col, 6 - vehicle.size), vehicle_orientation))
                    else:
                        new_optional_locations.append((min(row, 6 - vehicle.size), col, vehicle_orientation))
            vehicles_to_optional_locations[vehicle] = new_optional_locations

        if vehicles[0] in vehicles_to_optional_locations:
            vehicles_to_optional_locations[vehicles[0]] = filter_by_red_car(vehicles_to_optional_locations[vehicles[0]])
        vehicles_to_optional_locations = filter_by_conflicts(vehicles_to_optional_locations)
        vehicles_to_optional_locations = filter_by_edges(vehicles_to_process, vehicles_to_optional_locations, 0.03)

        vehicles_to_optional_locations = dict(sorted(vehicles_to_optional_locations.items(), key=lambda key: len(key)))
        for option in product(*vehicles_to_optional_locations.values()):
            is_legal = True
            backup_matrix = self.board_matrix.copy()
            for index, vehicle in enumerate(vehicles_to_optional_locations.keys()):
                row, col, vehicle_orientation = option[index]
                if self.is_available(vehicle, row, col, vehicle_orientation):
                    self.add_vehicle_to_board(vehicle, row, col, vehicle_orientation)
                else:
                    is_legal = False
                    self.board_matrix = backup_matrix
                    break
            if is_legal:
                vehicles_to_optional_locations = {}
                break

        while len(vehicles_to_optional_locations) != 0:
            vehicle = next(iter(vehicles_to_optional_locations))
            row, col, vehicle_orientation = vehicles_to_optional_locations[vehicle][0]
            if self.is_available(vehicle, row, col, vehicle_orientation):
                self.add_vehicle_to_board(vehicle, row, col, vehicle_orientation)
            vehicles_to_optional_locations.pop(vehicle)
            vehicles_to_optional_locations = filter_by_conflicts(vehicles_to_optional_locations)
            vehicles_to_optional_locations = dict(
                sorted(vehicles_to_optional_locations.items(), key=lambda key: len(key)))
