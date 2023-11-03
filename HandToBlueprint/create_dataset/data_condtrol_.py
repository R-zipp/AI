import cv2
import os
import numpy as np
import detect
import easyocr



class CreateDataset():
    def __init__(self) -> None:
        self.data = None
    
    
    def data_load(self, directory=None, file=None):
        if directory and file:
            raise Exception("You must choose between a directory and a file.")
        
        if directory:
            file_list = os.listdir(directory)
            self.data = [os.path.join(directory, name) for name in file_list]
        elif file:
            self.data = file
        
        
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
        
        
    def get_blueprint(self, img, padding_percent=0.2):
        temp_img = img.copy()
        gray = cv2.cvtColor(temp_img,cv2.COLOR_BGR2GRAY)
        contour, c_img = detect.outer_contours(gray, temp_img, color=(255,0,0))

        point_1 = (min([i[0][0] for i in contour]), min([i[0][1] for i in contour]))
        point_2 = (max([i[0][0] for i in contour]), max([i[0][1] for i in contour]))
        
        rect = img[point_1[1]:point_2[1], point_1[0]:point_2[0]]
        
        height, width, _ = rect.shape

        padding_width = int(width * padding_percent)
        padding_height = int(height * padding_percent)

        blueprint_img = cv2.copyMakeBorder(rect,
                                        padding_height,
                                        padding_height,
                                        padding_width,
                                        padding_width,
                                        cv2.BORDER_CONSTANT,
                                        value=[255, 255, 255])

        return blueprint_img


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
    
        
    def image_save(self, file_path, output_dir='./output', base_filename = 'image', index=0):
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        except OSError:
            print("Error: Failed to create the directory.")
        
        file_name = sum([i.split('\\') for i in file_path.split('/')], [])[-1]
        filename, extension = os.path.splitext(file_name)
        extension = '.png'
        
        new_filename = f"{base_filename}_{index:04d}{extension}"
        
        while os.path.exists(os.path.join(output_dir, new_filename)):
            index += 1
            new_filename = f"{base_filename}_{index:04d}{extension}"
        
        print(f'>> Save image : {new_filename}')
        cv2.imwrite(os.path.join(output_dir, new_filename), self.image)
    
    
    def parameter_setting(self, limit=150, aspect_ratio = 3/2):
        self.limit = limit
        self.aspect_ratio = aspect_ratio
        
        
    def process(self, file, save):
        self.image = cv2.imread(file)
        cv2.imwrite('temp.PNG', self.image)
        # self.image = self.make_binary(self.image, limit=self.limit)
        # self.image = self.remove_text(self.image)
        self.image = self.cutting_image(self.image)

        self.image = self.get_blueprint(self.image)
        self.image = self.proportion_control(self.image, aspect_ratio=self.aspect_ratio)
        self.image = self.resize_image(self.image)
        
        if save:
            self.image_save(file, output_dir='./no_ocr_binary')
        
    
    def run(self, save=False):
        if type(self.data)==str:
            file = self.data
            self.process(file, save)
                
        elif type(self.data)==list:
            for file in self.data[:]:
                self.process(file, save)
                
        

if __name__ == '__main__':
    create_dataset = CreateDataset()
    
    directory = 'data/raw_data'
    file = 'data/raw_data/image_217.jpg'
    
    # create_dataset.data_load(file=file)
    create_dataset.data_load(directory=directory)
    create_dataset.parameter_setting(limit=130, aspect_ratio=1/1)
    result = create_dataset.run(save=True)
