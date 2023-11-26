from PIL import Image
import os
import subprocess

from Lib.data_condtrol import CreateDataset
from Lib.generate_blueprint import BlueprintGenerator
import Lib.const as const
from blueprint_to3D import BLueprintTo3D


preprocessing = CreateDataset()
generator = BlueprintGenerator(const.MODEL_PATH)
bLueprint_to_3D = BLueprintTo3D()

    
class ImageToFBX():
    def __init__(self):
        self.url = const.BLUEPRINT_TO_BLEND_SERVER_URL
    
    
    def handimg_to_fbx(self, origin_image):
        # Image generating
        generator.data_load(image=origin_image)
        generator.parameter_setting(
                                want_img='all', 
                                add_origin=False, 
                                output_dir='./Statics/generate_img',
                                output_name=self.name,
                                new_width=700)
        generating_result, result_img = generator.run(save=True)
        
        return generating_result, result_img


    def blueprint_to_fbx(self, origin_image):
        # Preprocessing
        preprocessing.data_load(image=origin_image)
        preprocessing.parameter_setting(
                                        limit=130, 
                                        aspect_ratio=1/1, 
                                        output_dir='./Statics/preprocessing_img',
                                        new_width=900,
                                        padding_percent=0.15, 
                                        output_name=self.name,
                                        same_name=bool(self.name))
        preprocessing_result, result_img = preprocessing.run(save=True)
        
        return preprocessing_result, result_img
            
    
    def bpy_subprocess(self, blend_path, area_size):
        blender_script = 'Lib/fbx_converter.py'
        size_multiplier = round(self.size / area_size, 1) if self.size else 1

        os.environ['BLEND_PATH'] = str(blend_path)
        os.environ['SIZE_MULTIPLIER'] = str(size_multiplier)
        os.environ['WALLPAPER_NO'] = str(self.wallpaper_no)
        
        blender_command = [
                            'C:/Program Files/Blender Foundation/Blender 3.6/blender.exe',
                            '-b',
                            '--python', blender_script
                            ]
        
        process = subprocess.run(blender_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(process.stdout.decode())
        if 'Error' in process.stdout.decode():
            print(process.stdout.decode())
            raise Exception("Blender subprocess error")
        else:
            result = process.stdout.decode().split('\r\n')
            fbx_path = [name for name in result if 'result' in name][0].split(' ')[-1]
            
            print(f'convert successfully!   >> {fbx_path}')
            
            return fbx_path
                        
    
    def process(self, preprocessing_result):
        # blueprint to blend file
        blend_path, area_size = bLueprint_to_3D.make_blend(preprocessing_result)
        
        fbx_file_path = self.bpy_subprocess(blend_path, area_size)
        
        return fbx_file_path
            
            
    def run(self, img_type, image, name=None, size=None, wallpaper_no=None):
        self.size = size
        self.name = name
        self.wallpaper_no = wallpaper_no
        
        # mode select
        if img_type == 'HANDIMG':
            preprocessing_result, result_img = self.handimg_to_fbx(image)
            fbx_file = self.process(preprocessing_result)
            
        elif img_type == 'FLOORPLAN':
            preprocessing_result, result_img = self.blueprint_to_fbx(image)
            fbx_file = self.process(preprocessing_result)
            
        return fbx_file



if __name__ == '__main__':
    ItoFBX = ImageToFBX()
    
    img_type = ["HANDIMG", "FLOORPLAN"]
    
    # img_path = 'statics/Images/Original/image_038.jpg'
    # img_path = 'KakaoTalk_20231120_102837071.jpg'
    img_path = 'Statics/test_2.png'
    name = img_path.split('/')[-1]
    image = Image.open(img_path)

    fbx_file = ItoFBX.run(img_type[0], image, name=name, size=28*3.3)

    # img_dir = 'statics/Images/Original'
    # img_list = os.listdir(img_dir)
    
    # cnt = 0
    # for img_name in img_list[1:2]:
    #     name = img_name
    
    #     image = Image.open(os.path.join(img_dir, img_name))
    
    #     fbx_file = ItoFBX.run(img_type[1], image, name=name, size=32*3.3)
    #     if fbx_file:
    #         cnt += 1
        
    # print(f'cnt : {cnt}')