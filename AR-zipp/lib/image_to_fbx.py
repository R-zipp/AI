from preprocessing import PreProcessing


class ImageToFBX():
    def __init__(self) -> None:
        pass


    def image_to_fbx(self):
        ouput_path = 'Images/After_preprocessing'
        img_path = "Images/Original/Test_img1.jpg"

        preprocessing = PreProcessing()
        preprocessing.run(img_path, ouput_path)