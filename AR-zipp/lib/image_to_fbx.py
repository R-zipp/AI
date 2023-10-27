import os
import requests
import time

from lib.preprocessing import PreProcessing
from lib.blend_to_fbx import BlendToFBX

preprocessing = PreProcessing()
converter = BlendToFBX()


class ImageToFBX():
    def __init__(self) -> None:
        pass

    def image_to_fbx(self, file_path):
        # Preprocessing
        ouput_path = 'statics/Images/After_preprocessing'
        preprocessing.run(file_path)
        preprocessing_result = preprocessing.file_save(ouput_path)

        # Image to blend file
        url = 'http://127.0.0.1:8001/blueprint_to_3D'

        data = {'ImagePath': preprocessing_result}

        for i in range(3):
            response = requests.post(url, json=data)
            print(f'Status Code: {response.status_code}  /  Response Content : {response.text}')
            if response.status_code == 200:
                break

        if response.status_code == 200:
            time.sleep(0.5)
        #     # Blend to fbx converter
            blend_name = response.text.replace('"','')
            blend_path = f"statics/blend_file/{blend_name}"

            fbx_dir = 'statics/fbx_file'
            fbx_file = converter.blend_to_fbx(blend_path, fbx_dir)

            print('convert successfully!')
            return fbx_file
        else:
            print(f'make bled error : {preprocessing_result}')
    

    def image_to_fbx_test(self, blend_name):
        # Preprocessing
        # ouput_path = 'statics/Images/After_preprocessing'
        # preprocessing.run(file_path)
        # preprocessing_result = preprocessing.file_save(ouput_path)

        # Image to blend file
        # url = 'http://127.0.0.1:8001/blueprint_to_3D'

        # data = {'ImagePath': preprocessing_result}

        # for i in range(3):
        #     response = requests.post(url, json=data)
        #     print(f'Status Code: {response.status_code}  /  Response Content : {response.text}')
        #     if response.status_code == 200:
        #         break


        # Blend to fbx converter
        try:
            blend_path = f"statics/blend_file/{blend_name}"

            fbx_dir = 'statics/fbx_file'
            converter.blend_to_fbx(blend_path, fbx_dir)

            print('convert successfully!')
        except:
            print(f'make bled error : {blend_name}')



if __name__ == '__main__':
    ItoFBX = ImageToFBX()

    # file_dir = 'statics\\Images\\Original'
    # file_list = os.listdir(file_dir)

    # file_path = str(file_dir+'\\'+'image_000.jpg')
    # ItoFBX.image_to_fbx(file_path)

    # for file in file_list[:]:
    #     file_path = str(file_dir+'\\'+file)
    #     ItoFBX.image_to_fbx(file_path)


    
    blend_dir = "statics/blend_file"
    blend_list = os.listdir(blend_dir)

    for name in blend_list[:20]:
        ItoFBX.image_to_fbx_test(name)
        time.sleep(1)