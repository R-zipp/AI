import ast
import os
import numpy as np
import math

import BlueprintToBlendLIb.const as const


def calculate_floor_size(directory):
    data_path = const.BASE_PATH
    coor_data = os.path.join(data_path, directory, 'floor_verts.txt')
    
    with open(coor_data, "r") as f:
        coordinates = ast.literal_eval(f.read())

    n = len(coordinates)
    area = 0.0

    for i in range(n):
        j = (i + 1) % n
        area += coordinates[i][0] * coordinates[j][1]
        area -= coordinates[j][0] * coordinates[i][1]

    area = abs(area) / 2.0
    
    return round(area, 1)
    

def rotation_coor(coor):
    theta = math.radians(-90)
    rotation_matrix = np.array([
                                [math.cos(theta), -math.sin(theta), 0],
                                [math.sin(theta), math.cos(theta), 0],
                                [0, 0, 1]
                                ])
    rotated_point = rotation_matrix.dot(coor)
    
    return rotated_point


def reflect_x_axis(point):
    reflect = point * [1, -1, 1]
    return reflect


def calculate_centroid_3d(directory):
    data_path = const.BASE_PATH
    coor_data = os.path.join(data_path, directory, 'room_verts.txt')

    with open(coor_data, "r") as f:
        coordinates = ast.literal_eval(f.read())
        
    # centroid = [np.mean(np.array(coors), axis=0).tolist() for coors in coordinates]
    centroid = []
    for coors in coordinates:
        mean = np.mean(np.array(coors), axis=0)
        retate_coor = rotation_coor(mean)
        coor = reflect_x_axis(retate_coor)
        centroid.append(coor.tolist())
    
    return centroid



if __name__ == '__main__':

    # directory = 'gen_img'
    # area_size = calculate_floor_size(directory, out_type='pyeong')
    # print(area_size)
    
    # Example usage
    example_coordinates = [
        [6.61, 5.6, 0.999],
        [6.62, 5.61, 0.999],
        [6.62, 6.44, 0.999],
        [7.85, 6.44, 0.999],
        [7.85, 5.73, 0.999],
        [6.91, 5.73, 0.999],
        [6.9, 5.72, 0.999],
        [6.9, 5.6, 0.999]
    ]

    centroid = calculate_centroid_3d(example_coordinates)
    print(centroid)