import os
from BlueprintToBlendLIb import (
    const,
    execution,
    create_blender_project    
)
from BlueprintToBlendLIb.floorplan import new_floorplan
from BlueprintToBlendLIb.calculate_floor_size import calculate_floor_size


class BLueprintTo3D():
    def __init__(self):
        self.target_folder = const.TARGET_PATH
        self.data_paths = list()


    def make_blend(self, img_path):
        print("")
        print("Creates blender project")

        floorplans = new_floorplan(img_path)

        base_name, extension = os.path.splitext(img_path.split('\\')[-1])
        
        data_paths = [execution.simple_single(floorplans, show=False, file_name=base_name)]
        blender_project_path = create_blender_project.create_blender_project(data_paths, self.target_folder, name=base_name)

        area_size = calculate_floor_size(base_name)
        
        return blender_project_path, area_size


if __name__ == "__main__":
    img_path = "Statics/Test_img/OCR_img.png"
    bLueprint_to_3D = BLueprintTo3D()
    project_path = bLueprint_to_3D.make_blend(img_path)
    print(project_path)