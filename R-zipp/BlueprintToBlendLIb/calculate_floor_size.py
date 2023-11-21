import ast
import os

import BlueprintToBlendLIb.const as const

def calculate_floor_size(directory, out_type='square meter'):
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
    
    if out_type == 'square meter':
        return round(area, 1)
    elif out_type == 'pyeong':
        return round(area * 0.3025, 1)


if __name__ == '__main__':

    directory = 'gen_img'
    # area_size = calculate_floor_size(directory)
    area_size = calculate_floor_size(directory, out_type='pyeong')
    print(area_size)