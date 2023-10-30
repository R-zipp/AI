import os
from PIL import Image

def merge_images(folder1, folder2, output_folder):
    # 폴더 안의 jpg 파일 리스트 가져오기
    folder1_files = [f for f in os.listdir(folder1) if f.endswith('.jpg')]
    folder2_files = [f for f in os.listdir(folder2) if f.endswith('.jpg')]

    # 두 폴더 안에 같은 이름의 jpg 파일이 있는지 확인
    common_files = set(folder1_files).intersection(folder2_files)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in common_files:
        # 두 이미지 불러오기
        img1 = Image.open(os.path.join(folder1, filename))
        img2 = Image.open(os.path.join(folder2, filename))

        # 두 이미지를 양옆으로 붙이기
        merged_img = Image.new('RGB', (img1.width + img2.width, img1.height))
        merged_img.paste(img1, (0, 0))
        merged_img.paste(img2, (img1.width, 0))

        # 이미지 크기를 512x256으로 변경
        resized_img = merged_img.resize((4096, 2048))

        # 결과 이미지 저장
        resized_img.save(os.path.join(output_folder, filename))

folder1_path = './a/' # 첫 번째 폴더 경로
folder2_path = './b/' # 두 번째 폴더 경로
output_folder_path = './change_image_2048/' # 출력 폴더 경로

merge_images(folder1_path, folder2_path, output_folder_path)
