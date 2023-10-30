from PIL import Image
import os
 
path_dir = './change_images'
 
file_list = os.listdir(path_dir)

for name in file_list:
    image = Image.open('./change_images/' + name)
    rgb_image = image.convert("RGB")
    rgb_image = rgb_image.resize((2500, 2500))
    rgb_image.save('./change_images2_jpg/' + name[:-4] + '.jpg')
