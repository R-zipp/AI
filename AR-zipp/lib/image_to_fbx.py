import os
import requests
import time

from lib.preprocessing import PreProcessing
from lib.blend_to_fbx import BlendToFBX
from lib.data_condtrol_ import CreateDataset

preprocessing = PreProcessing()
converter = BlendToFBX()
create_dataset = CreateDataset()


class ImageToFBX():
    def __init__(self) -> None:
        pass

    def image_to_fbx_old(self, file_path):
        # Preprocessing
        ouput_path = 'statics/Images/After_preprocessing'
        preprocessing.run(file_path)
        preprocessing_result = preprocessing.file_save(ouput_path)

        # Image to blend file
        url = 'http://127.0.0.1:8001/blueprint_to_3D'

        data = {'ImagePath': preprocessing_result}

        response = requests.post(url, json=data)
        print(f'Status Code: {response.status_code}  /  Response Content : {response.text}')

        if response.status_code == 200:
            # Blend to fbx converter
            blend_name = response.text.replace('"','')
            blend_path = f"statics/blend_file/{blend_name}"

            fbx_dir = 'statics/fbx_file'
            fbx_file = converter.blend_to_fbx(blend_path, fbx_dir)

            print('convert successfully!')
            return fbx_file
        else:
            print(f'make bled error : {preprocessing_result}')
    

    def image_to_fbx(self, file_path):
        # Preprocessing
        create_dataset.data_load(file=file_path)
        create_dataset.parameter_setting(
                                        limit=110, 
                                        aspect_ratio=1/1, 
                                        output_dir='./statics/uploads',
                                        new_width=800,
                                        padding_percent=0.1)
        preprocessing_result, result_img = create_dataset.run(save=True)

        # Image to blend file
        url = 'http://127.0.0.1:8001/blueprint_to_3D'

        data = {'ImagePath': preprocessing_result}

        response = requests.post(url, json=data)
        print(f'Status Code: {response.status_code}  /  Response Content : {response.text}')

        # Blend to fbx converter
        if response.status_code == 200:
            blend_name = response.text.replace('"','')
            blend_path = f"statics/blend_file/{blend_name}"

            fbx_dir = 'statics/fbx_file'
            fbx_file_path = converter.blend_to_fbx(blend_path, fbx_dir)

            print('convert successfully!')
            return fbx_file_path
        else:
            print(f'make bled error : {preprocessing_result}')


if __name__ == '__main__':
    ItoFBX = ImageToFBX()

    file = 'statics/Images/Original/image_000.jpg'
    directory = 'statics/Images/Original'
    file_list = os.listdir(directory)
    for file_name in file_list[:20]:
        fbx_file = ItoFBX.image_to_fbx(os.path.join(directory, file_name))
        print('')
    # print(fbx_file)