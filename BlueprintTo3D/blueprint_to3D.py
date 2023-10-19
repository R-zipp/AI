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
        self.floorplans = []

        print("")
        print("Creates blender project")
        print("")

        config_path = "./Configs/default.ini"

        config = configparser.ConfigParser()
        config.read(config_path)
        config.set('IMAGE', 'image_path', f'\"{img_path}\"')

        with open(config_path, 'w') as configfile:
            config.write(configfile)

        self.floorplans.append(new_floorplan(config_path))

        IO.clean_data_folder(self.data_folder)

        if len(self.floorplans) > 1:
            data_paths.append(execution.simple_single(f) for f in self.floorplans)
        else:
            data_paths = [execution.simple_single(self.floorplans[0])]
        print("")

        if isinstance(data_paths[0], list):
            for paths in data_paths:
                blender_project_path = create_blender_project.create_blender_project(paths, self.target_folder)
        else:
            blender_project_path = create_blender_project.create_blender_project(data_paths, self.target_folder)

        return blender_project_path


if __name__ == "__main__":
    img_path = "Images/Test_img/OCR_img.png"
    bLueprint_to_3D = BLueprintTo3D()
    project_path = bLueprint_to_3D.make_blend(img_path)
    print(project_path)