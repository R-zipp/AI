import cv2
import numpy as np



def outer_contours(detect_img, output_img=None, color=[255, 255, 255], thickness=3):
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
        output_img = cv2.drawContours(output_img, [approx], -1, color, thickness)
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


def precise_boxes(detect_img, output_img=None, color=[100, 100, 0], thickness=2):
    PRECISE_BOXES_ACCURACY = 0.001

    res = []

    contours, _ = cv2.findContours(
        detect_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for cnt in contours:
        epsilon = PRECISE_BOXES_ACCURACY * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        if output_img is not None:
            output_img = cv2.drawContours(output_img, [approx], -1, color, thickness)
        res.append(approx)

    return res, output_img