import cv2
import numpy as np
import easyocr
import os
import detect as detect



def get_padding(image):
    image_copy = image.copy()
    height, width = image_copy.shape[:2]
    gray = cv2.cvtColor(image_copy,cv2.COLOR_BGR2GRAY)
    contour, c_img = detect.outer_contours(gray, image_copy, color=(255,0,0))

    x_min, x_max = min([i[0][0] for i in contour]), max([i[0][0] for i in contour])
    y_min, y_max = min([i[0][1] for i in contour]), max([i[0][1] for i in contour])

    padding_top, padding_left, padding_right, padding_bottom = y_min, x_min, width-x_max, height-y_max

    return [padding_top, padding_left, padding_right, padding_bottom]


def get_contour_size(image):
    image_copy = image.copy()
    gray = cv2.cvtColor(image_copy,cv2.COLOR_BGR2GRAY)
    contour, c_img = detect.outer_contours(gray, image_copy, color=(255,0,0))

    x_min, x_max = min([i[0][0] for i in contour]), max([i[0][0] for i in contour])
    y_min, y_max = min([i[0][1] for i in contour]), max([i[0][1] for i in contour])

    return [x_max-x_min, y_max-y_min]


def resize_with_padding(img, scale_percent=60):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    background = np.ones_like(img) * 255  # 모든 픽셀을 흰색으로 설정합니다.

    center_x = (img.shape[1] - width) // 2
    center_y = (img.shape[0] - height) // 2

    # 배경 이미지 위에 리사이즈된 이미지를 붙입니다.
    background[center_y:center_y+height, center_x:center_x+width] = resized

    return background



class PreProcessing():
    def __init__(self) -> None:
        pass


    def run(self, img_path):
        self.img = cv2.imread(img_path)

        self.name, self.extension = img_path.split("/")[-1].split(".")
        
        self.img = self.make_binary_img(self.img)
        self.img = self.remove_text(self.img)
        self.img = self.add_img_padding(self.img)


    def make_binary_img(self, image, save=False):
        binary_img = image.copy()

        lower_bound = np.array([0, 0, 0], dtype=np.uint8)
        upper_bound = np.array([150, 150, 150], dtype=np.uint8)
        mask = cv2.inRange(binary_img, lower_bound, upper_bound)
        binary_img[np.where(mask == 0)] = [255, 255, 255]

        print(f'Make binary image done')
        return binary_img


    def remove_text(self, image, save=False):
        OCR_img = self.img.copy()

        reader = easyocr.Reader(['ko','en'])
        results = reader.readtext(OCR_img)

        for result in results:
            check_int = any([True if isinstance(i, np.int32) else False for i in result[0][0] + result[0][2]])
            if check_int:
                cv2.rectangle(OCR_img, result[0][0], result[0][2], (255, 255, 255), -1)

        print(f'Remove text done')
        return OCR_img


    def add_img_padding(self, image):
        padding_img = image.copy()

        contour_size = get_contour_size(padding_img)

        height, width = padding_img.shape[:2]
        default_size = [width*0.65, height*0.8]

        if default_size[0] < contour_size[0] or default_size[1] < contour_size[1]:
            ratio = min([default_size[0] / contour_size[0], default_size[1] / contour_size[1]])*100

            padding_img = resize_with_padding(padding_img, scale_percent=ratio)

        print(f'Add padding done')
        return padding_img


    def file_save(self, output_path):
        self.output_path = output_path

        print(f'Save preprocessing iamge : {self.name}_pre.png')
        cv2.imwrite(os.path.join(self.output_path, f'{self.name}_pre.png'), self.img)

        return self.output_path + '/' + f'{self.name}_pre.png'




if __name__ == "__main__":
    ouput_path = 'statics/Images/After_preprocessing'
    img_path = "statics/Images/Original/Test_img1.jpg"

    preprocessing = PreProcessing()
    preprocessing.run(img_path)
    preprocessing.file_save(ouput_path)