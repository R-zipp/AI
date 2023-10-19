import cv2
import numpy as np
import easyocr
from PIL import Image
from IPython.display import display
import os


class PreProcessing():
    def __init__(self) -> None:
        pass


    def run(self, img_path, output_path):
        self.img = cv2.imread(img_path)
        self.output_path = output_path

        self.name, self.extension = img_path.split("\\")[-1].split(".")
        
        self.make_binary_img()
        self.remove_text(save=True)


    def make_binary_img(self, save=False):
        lower_bound = np.array([0, 0, 0], dtype=np.uint8)
        upper_bound = np.array([150, 150, 150], dtype=np.uint8)
        mask = cv2.inRange(self.img, lower_bound, upper_bound)
        self.img[np.where(mask == 0)] = [255, 255, 255]

        if save:
            print(f'Make binary image done : {self.name}_bi.png')
            cv2.imwrite(os.path.join(self.output_path, f'{self.name}_bi.png'), self.img)
        else:
            print(f'Make binary image done : not save')


    def remove_text(self, save=False):
        reader = easyocr.Reader(['ko','en'])
        results = reader.readtext(self.img)

        OCR_img = self.img.copy()

        for result in results:
            cv2.rectangle(OCR_img, result[0][0], result[0][2], (255, 255, 255), -1)

        if save:
            print(f'Remove text done : {self.name}_OCR.png')
            cv2.imwrite(os.path.join(self.output_path, f'{self.name}_OCR.png'), OCR_img)
        else:
            print(f'Remove text done : not save')

    
    def file_save_path(self, target):
        if target == 'binary':
            return os.path.join(self.output_path, f'{self.name}_bi.png')
        elif target == 'OCR':
            return os.path.join(self.output_path, f'{self.name}_OCR.png')
        else:
            raise ValueError("You can only choose 'binary' or 'OCR'")


if __name__ == "__main__":
    ouput_path = 'statics/Images/After_preprocessing'
    img_path = "statics/Images/Original/Test_img1.jpg"

    preprocessing = PreProcessing()
    preprocessing.run(img_path, ouput_path)