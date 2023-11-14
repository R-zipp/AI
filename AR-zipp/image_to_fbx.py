import json
import requests
from PIL import Image

from lib.data_condtrol import CreateDataset
from lib.generate_blueprint import BlueprintGenerator
from lib.fbx_converter import BlendToFBX
import lib.const as const


converter = BlendToFBX()
preprocessing = CreateDataset()
generator = BlueprintGenerator(const.MODEL_PATH)


class ImageToFBX():
    def __init__(self):
        self.url = const.BLUEPRINT_TO_BLEND_SERVER_URL
    
    
    def handimg_to_fbx(self, origin_image):
        # Image generating
        generator.data_load(image=origin_image)
        generator.parameter_setting(
                                want_img='all', 
                                add_origin=False, 
                                output_dir='./statics/generate_img',
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
                                        output_dir='./statics/preprocessing_img',
                                        new_width=700,
                                        padding_percent=0.15, 
                                        output_name=self.name,
                                        same_name=bool(self.name))
        preprocessing_result, result_img = preprocessing.run(save=True)
        
        return preprocessing_result, result_img
            
    
    def process(self, preprocessing_result):
        # blueprint to blend file
        data = {'ImagePath': preprocessing_result}
        response = requests.post(self.url, json=data)
        BtoB_result = json.loads(response.text)
        
        print(f'Status Code: {response.status_code}')
        print(f'Response Content : {response.text}')
        
        # Blend to fbx converter
        if response.status_code == 200:
            blend_path = f"statics/blend_file/{BtoB_result['blend_name']}"

            size_multiplier = round(self.size / BtoB_result['size'], 1) if self.size else 1
            fbx_dir = 'statics/fbx_file'
            fbx_file_path = converter.blend_to_fbx(
                                                    blend_path, 
                                                    fbx_dir, 
                                                    texture_name='plaster_2K', 
                                                    size_multiplier=size_multiplier, 
                                                    desired_height=3,
                                                    tiling_factor=(0.1, 0.1)
                                                    ).replace('\\', '/')

            print(f'convert successfully!   >> {fbx_file_path}')
            return fbx_file_path
        else:
            print(f'make bled error : {preprocessing_result}')
    
    
    def run(self, img_type, image, name=None, size=None):
        self.size = size
        self.name = name
        
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

    # img_path = './statics/Images/Original/image_038.jpg'
    # img_path = 'statics/Images/SD_output_2/cycle_1/image_1130_(01).png'
    img_path = 'statics/Images/SD_output_2/cycle_1/image_1147_(01).png'
    # img_path = './statics/Images/image_1171_(06).png'
    name = img_path.split('/')[-1]
    
    image = Image.open(img_path)
    
    fbx_file = ItoFBX.run(img_type[0], image, name=name, size=32*3.3)