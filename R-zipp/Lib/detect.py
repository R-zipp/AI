import cv2
import numpy as np
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from BlueprintToBlendLIb import image
from BlueprintToBlendLIb import const
from BlueprintToBlendLIb import image
from BlueprintToBlendLIb import calculate
from BlueprintToBlendLIb import transform
import math


def outer_contours(detect_img, output_img=None, color=[255, 255, 255]):
    OUTER_CONTOURS_TRESHOLD = [230, 255]
    PRECISE_BOXES_ACCURACY = 0.001

    ret, thresh = cv2.threshold(
        detect_img,
        OUTER_CONTOURS_TRESHOLD[0],
        OUTER_CONTOURS_TRESHOLD[1],
        cv2.THRESH_BINARY_INV,
    )

    contours, hierarchy = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    largest_contour_area = 0
    for cnt in contours:
        if cv2.contourArea(cnt) > largest_contour_area:
            largest_contour_area = cv2.contourArea(cnt)
            largest_contour = cnt

    epsilon = PRECISE_BOXES_ACCURACY * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    if output_img is not None:
        output_img = cv2.drawContours(output_img, [approx], 0, color)
    return approx, output_img


def wall_filter(gray):
    WALL_FILTER_TRESHOLD = [0, 255]
    WALL_FILTER_KERNEL_SIZE = (3, 3)
    WALL_FILTER_MORPHOLOGY_ITERATIONS = 2
    WALL_FILTER_DILATE_ITERATIONS = 1
    WALL_FILTER_DISTANCE = 5
    WALL_FILTER_DISTANCE_THRESHOLD = [0.5, 0.2]
    WALL_FILTER_MAX_VALUE = 255
    WALL_FILTER_THRESHOLD_TECHNIQUE = 0

    _, thresh = cv2.threshold(
        gray,
        WALL_FILTER_TRESHOLD[0],
        WALL_FILTER_TRESHOLD[1],
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    # noise removal
    kernel = np.ones(WALL_FILTER_KERNEL_SIZE, np.uint8)
    opening = cv2.morphologyEx(
        thresh,
        cv2.MORPH_OPEN,
        kernel,
        iterations=WALL_FILTER_MORPHOLOGY_ITERATIONS,
    )

    sure_bg = cv2.dilate(
        opening, kernel, iterations=WALL_FILTER_DILATE_ITERATIONS
    )

    dist_transform = cv2.distanceTransform(
        opening, cv2.DIST_L2, WALL_FILTER_DISTANCE
    )
    ret, sure_fg = cv2.threshold(
        WALL_FILTER_DISTANCE_THRESHOLD[0] * dist_transform,
        WALL_FILTER_DISTANCE_THRESHOLD[1] * dist_transform.max(),
        WALL_FILTER_MAX_VALUE,
        WALL_FILTER_THRESHOLD_TECHNIQUE,
    )

    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    return unknown


def __corners_and_draw_lines(img, corners_threshold, room_closing_max_length):
    """
    Finds corners and draw lines from them
    Help function for finding room
    @Param image input image
    @Param corners_threshold threshold for corner distance
    @Param room_closing_max_length threshold for room max size
    @Return output image
    """
    # Detect corners (you can play with the parameters here)
    kernel = np.ones(const.PRECISE_HARRIS_KERNEL_SIZE, np.uint8)

    dst = cv2.cornerHarris(
        img,
        const.PRECISE_HARRIS_BLOCK_SIZE,
        const.PRECISE_HARRIS_KSIZE,
        const.PRECISE_HARRIS_K,
    )
    dst = cv2.erode(dst, kernel, iterations=const.PRECISE_ERODE_ITERATIONS)
    corners = dst > corners_threshold * dst.max()

    # Draw lines to close the rooms off by adding a line between corners on the same x or y coordinate
    # This gets some false positives.
    # You could try to disallow drawing through other existing lines for example.
    for y, row in enumerate(corners):
        x_same_y = np.argwhere(row)
        for x1, x2 in zip(x_same_y[:-1], x_same_y[1:]):

            if x2[0] - x1[0] < room_closing_max_length:
                color = 0
                cv2.line(img, (x1[0], y), (x2[0], y), color, 1)

    for x, col in enumerate(corners.T):
        y_same_x = np.argwhere(col)
        for y1, y2 in zip(y_same_x[:-1], y_same_x[1:]):
            if y2[0] - y1[0] < room_closing_max_length:
                color = 0
                cv2.line(img, (x, y1[0]), (x, y2[0]), color, 1)
    return img


def find_rooms(
    img,
    noise_removal_threshold=const.FIND_ROOMS_NOISE_REMOVAL_THRESHOLD,
    corners_threshold=const.FIND_ROOMS_CORNERS_THRESHOLD,
    room_closing_max_length=const.FIND_ROOMS_CLOSING_MAX_LENGTH,
    gap_in_wall_min_threshold=const.FIND_ROOMS_GAP_IN_WALL_MIN_THRESHOLD,
):
    """
    src: https://stackoverflow.com/questions/54274610/crop-each-of-them-using-opencv-python

    @param img: grey scale image of rooms, already eroded and doors removed etc.
    @param noise_removal_threshold: Minimal area of blobs to be kept.
    @param corners_threshold: Threshold to allow corners. Higher removes more of the house.
    @param room_closing_max_length: Maximum line length to add to close off open doors.
    @param gap_in_wall_threshold: Minimum number of pixels to identify component as room instead of hole in the wall.
    @return: rooms: list of numpy arrays containing boolean masks for each detected room
             colored_house: A colored version of the input image, where each room has a random color.
    """
    assert 0 <= corners_threshold <= 1
    # Remove noise left from door removal

    mask = image.remove_noise(img, noise_removal_threshold)
    img = ~mask

    __corners_and_draw_lines(img, corners_threshold, room_closing_max_length)

    img, mask = image.mark_outside_black(img, mask)

    # Find the connected components in the house
    ret, labels = cv2.connectedComponents(img)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    unique = np.unique(labels)
    rooms = []
    for label in unique:
        component = labels == label
        if (
            img[component].sum() == 0
            or np.count_nonzero(component) < gap_in_wall_min_threshold
        ):
            color = 0
        else:
            rooms.append(component)
            color = np.random.randint(0, 255, size=3)
        img[component] = color
    return rooms, img


def precise_boxes(detect_img, output_img=None, color=[100, 100, 0]):
    PRECISE_BOXES_ACCURACY = 0.001

    res = []

    contours, _ = cv2.findContours(
        detect_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for cnt in contours:
        epsilon = PRECISE_BOXES_ACCURACY * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        if output_img is not None:
            output_img = cv2.drawContours(output_img, [approx], 0, color, 2)
        res.append(approx)

    return res, output_img