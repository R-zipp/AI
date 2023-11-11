import cv2
import os
import numpy as np
import easyocr
from PIL import Image

import lib.detect as detect


class CreateDataset():
    def __init__(self) -> None:
        self.data = None
    
    
    def remove_text(self, img):
        reader = easyocr.Reader(['ko','en'])
        results = reader.readtext(img)

        for result in results:
            start_point = result[0][0]
            end_point = result[0][2]
            
            check_int = any([True if isinstance(i, np.int32) else False for i in start_point + end_point])
            if check_int:
                cv2.rectangle(img, start_point, end_point, (255, 255, 255), -1)

        return img
    
    
    def cutting_image(self, img, pixel=200):
        height, width = img.shape[:2]
        if 3000 < height and 3000 < width:
            img = img[pixel:height-pixel, pixel:width-pixel]
        
        return img
    
    
    def make_binary(self, img, limit=150):
        lower_bound = np.array([0, 0, 0], dtype=np.uint8)
        upper_bound = np.array([limit, limit, limit], dtype=np.uint8)
        mask = cv2.inRange(img, lower_bound, upper_bound)
        img[np.where(mask == 0)] = [255, 255, 255]

        return img
    
    
    def make_grayscale(self, img):
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_image_3channel = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
        
        return gray_image_3channel
        
        
    def remake_padding(self, img, padding_percent=0.2):
        temp_img = img.copy()
        gray = cv2.cvtColor(temp_img,cv2.COLOR_BGR2GRAY)
        contour, c_img = detect.outer_contours(gray, temp_img, color=(255,0,0))

        point_1 = (min([i[0][0] for i in contour]), min([i[0][1] for i in contour]))
        point_2 = (max([i[0][0] for i in contour]), max([i[0][1] for i in contour]))
        
        rect = img[point_1[1]:point_2[1], point_1[0]:point_2[0]]
        
        height, width, _ = rect.shape

        padding_width = int(width * padding_percent)
        padding_height = int(height * padding_percent)

        padding_img = cv2.copyMakeBorder(rect,
                                        padding_height,
                                        padding_height,
                                        padding_width,
                                        padding_width,
                                        cv2.BORDER_CONSTANT,
                                        value=[255, 255, 255])

        return padding_img


    def proportion_control(self, img, aspect_ratio=16/9):
        original_height, original_width = img.shape[:2]
        original_aspect_ratio = original_width / original_height

        if original_aspect_ratio > aspect_ratio:
            new_width = original_width
            new_height = int(original_width / aspect_ratio)
            padding_top = (new_height - original_height) // 2
            padding_bottom = new_height - original_height - padding_top
            padding_left = padding_right = 0
        elif original_aspect_ratio < aspect_ratio:
            new_height = original_height
            new_width = int(original_height * aspect_ratio)
            padding_left = (new_width - original_width) // 2
            padding_right = new_width - original_width - padding_left
            padding_top = padding_bottom = 0
        else:
            padding_top = padding_bottom = padding_left = padding_right = 0

        padded_img = cv2.copyMakeBorder(img, padding_top, padding_bottom, padding_left, padding_right, cv2.BORDER_CONSTANT, value=[255, 255, 255])

        return padded_img


    def resize_image(self, img, new_width=1024):
        original_height, original_width = img.shape[:2]
        new_height = int((new_width * original_height) / original_width)

        resized_image = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

        return resized_image
    
        
    def image_save(self, image, filename, output_dir='./output', same_name=False, index=0):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError:
            print("Error: Failed to create the directory.")
        
        extension = '.png'
        
        if not same_name:
            filename = 'image'
            new_filename = f"{filename}_{index:04d}{extension}"
            
            while os.path.exists(os.path.join(output_dir, new_filename)):
                index += 1
                new_filename = f"{filename}_{index:04d}{extension}"
        else:
            # file_name = sum([i.split('\\') for i in file_path.split('/')], [])[-1]
            filename, extension_ = os.path.splitext(filename)
            new_filename = f"{filename}{extension}"
        
        print(f'>> Save image : {new_filename}')
        
        new_path = os.path.join(output_dir, new_filename)
        cv2.imwrite(new_path, image)
        
        return new_path

    
    def data_load(self, directory=None, file=None, image=None):
        cnt = len([i for i in [directory, file, image] if i])
        if cnt >= 2:
            raise Exception("You must choose only one type")
        
        if directory:
            file_list = os.listdir(directory)
            self.data = [os.path.join(directory, name) for name in file_list]
        elif file:
            self.data = file
        elif isinstance(image, Image.Image):
            self.data = image

    
    def parameter_setting(self, limit=150, 
                          aspect_ratio = 3/2, 
                          output_dir='./output', 
                          new_width=1024, 
                          padding_percent=0.2, 
                          output_name='image',
                          same_name=False):
        self.limit = limit
        self.aspect_ratio = aspect_ratio
        self.output_dir = output_dir
        self.new_width = new_width
        self.padding_percent = padding_percent
        self.same_name = same_name
        self.output_name = output_name
        
        
    def process(self, file, save=False):
        if isinstance(self.data, Image.Image):
            self.image = np.array(file)
        else:
            self.image = cv2.imread(file)
            self.output_name = sum([i.split('\\') for i in file.split('/')], [])[-1]

        cv2.imwrite('temp.PNG', self.image)
        self.image = self.make_binary(self.image, limit=self.limit)
        self.image = self.remove_text(self.image)
        # self.image = self.make_grayscale(self.image)
        self.image = self.cutting_image(self.image)

        self.image = self.remake_padding(self.image, padding_percent=self.padding_percent)
        self.image = self.proportion_control(self.image, aspect_ratio=self.aspect_ratio)
        self.image = self.resize_image(self.image, new_width=self.new_width)
        
        if save:
            new_path = self.image_save(self.image, self.output_name, output_dir=self.output_dir, same_name=self.same_name)
            
            return new_path, self.image
        else:
            return None, self.image
    
    
    def run(self, save=False):
        if type(self.data)==str:
            file = self.data
            new_path, result_img = self.process(file, save=save)
                
        elif type(self.data)==list:
            for file in self.data[:]:
                new_path, result_img = self.process(file, save=save)
                
        elif isinstance(self.data, Image.Image):
            file = self.data
            new_path, result_img = self.process(file, save=save)
            
        else:
            raise Exception('data type is wrong')
                
        print('Preprocessing done')
        return new_path, result_img
                
        

if __name__ == '__main__':
    create_dataset = CreateDataset()
    
    directory = 'statics/Images/Original'
    file = 'statics/Images/Original/image_000.jpg'
    
    create_dataset.data_load(file=file)
    # create_dataset.data_load(directory=directory)
    create_dataset.parameter_setting(
                                    limit=130, 
                                    aspect_ratio=1/1, 
                                    output_dir='./statics/uploads',
                                    new_width=800,
                                    same_name=False)
    result_img = create_dataset.run(save=True)
    