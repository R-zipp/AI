import os
from FloorplanToBlenderLib import (
    IO,
    config,
    const,
    execution,
    dialog,
    create_blender_project    
)
from FloorplanToBlenderLib.floorplan import new_floorplan
import configparser
from calculate_floor_size import calculate_floor_size


class BLueprintTo3D():
    def __init__(self):
        dialog.figlet()
        self.image_path = ""
        self.blender_install_path = ""
        self.data_folder = const.BASE_PATH
        self.blender_install_path = config.get_default_blender_installation_path()
        self.target_folder = const.TARGET_PATH
        self.image_paths = []
        self.program_path = os.path.dirname(os.path.realpath(__file__))
        self.blender_script_path = const.BLENDER_SCRIPT_PATH
        dialog.init()
        self.data_paths = list()
        
        dialog.end_copyright()


    def make_blend(self, img_path):
        print("")
        print("Creates blender project")

        config_path = "./Configs/default.ini"

        config = configparser.ConfigParser()
        config.read(config_path)
        config.set('IMAGE', 'image_path', f'\"{img_path}\"')

        with open(config_path, 'w') as configfile:
            config.write(configfile)

        floorplans = new_floorplan(config_path)

        # IO.clean_data_folder(self.data_folder)
        base_name, extension = os.path.splitext(img_path.split('/')[-1])
        print("")
        data_paths = [execution.simple_single(floorplans, file_name=base_name)]
        blender_project_path = create_blender_project.create_blender_project(data_paths, self.target_folder)

        area_size = calculate_floor_size(base_name)
        
        return blender_project_path, area_size


if __name__ == "__main__":
    img_path = "Images/Test_img/OCR_img.png"
    bLueprint_to_3D = BLueprintTo3D()
    project_path = bLueprint_to_3D.make_blend(img_path)
    print(project_path)