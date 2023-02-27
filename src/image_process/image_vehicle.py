import cv2

from dataclasses import dataclass
from operator import ior
from functools import reduce


@dataclass(frozen=True)
class VehicleImage:
    id: int
    name: str
    size: int
    color_ranges: tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...]

    def filter_color(self, image):
        """

        @param image: HSV
        @return:
        """
        masks = []
        for color_range in self.color_ranges:
            masks.append(cv2.inRange(image, *color_range))
        # bitwise-or between all masks
        return reduce(ior, masks)

    def find_vehicle(self, image, contour_area_threshold):
        """
        @param image:
        @param contour_area_threshold:
        @return:
        """
        vehicle_image = self.filter_color(image)
        ret, threshold = cv2.threshold(vehicle_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closing = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, rect_kernel)
        erosion = cv2.erode(closing, rect_kernel, iterations=3)
        contours = cv2.findContours(erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours[0]:
            contours = contours[0] if len(contours) == 2 else contours[1]
            contour = sorted(contours, key=cv2.contourArea, reverse=True)[0]
            if cv2.contourArea(contour) > contour_area_threshold:
                return cv2.boundingRect(contour)

