import os
from PIL import Image

def merge_images(folder1, folder2, output_folder, idx):
    # 폴더 안의 jpg 파일 리스트 가져오기
    folder1_files = [f for f in os.listdir(folder1) if f.endswith('.png')]
    folder2_files = [f for f in os.listdir(folder2) if f.endswith('.png')]

    # 두 폴더 안에 같은 이름의 jpg 파일이 있는지 확인
    common_files = set(folder1_files).intersection(folder2_files)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in list(common_files)[:]:
        # 두 이미지 불러오기
        img1 = Image.open(os.path.join(folder1, filename))
        img2 = Image.open(os.path.join(folder2, filename))

        # 두 이미지를 양옆으로 붙이기
        merged_img = Image.new('RGB', (img1.width + img2.width, img1.height))
        merged_img.paste(img1, (0, 0))
        merged_img.paste(img2, (img1.width, 0))
        merged_img = merged_img.convert('RGB')

        # 이미지 크기를 512x256으로 변경
        # resized_img = merged_img.resize((4096, 2048))

        # name_parts = filename.split('_')  # 먼저 파일 이름을 분할
        # name_parts.insert(1, 'c0')        # 'c0'을 리스트의 시작 부분에 삽입
        # new_name = '_'.join(name_parts) 
        new = int(filename.split('_')[-1].split('.')[0])
        new_name = f'image_c{idx}_{new:04d}.jpg'
        # print(new_name)
        # 결과 이미지 저장
        merged_img.save(os.path.join(output_folder, new_name))


if __name__ == '__main__':
    data_list = ['cycle_0', 'cycle_1', 'cycle_2', 'cycle_3', 'cycle_4']
    # data_list = ['cycle_0']
    
    print('run!')
    for idx, name in enumerate(data_list):
        folder1_path = './target/' # 두 번째 폴더 경로
        folder2_path = f'./stable_diffusion/{name}/' # 첫 번째 폴더 경로
        output_folder_path = './stable_diffusion_1108_v0/' # 출력 폴더 경로

        merge_images(folder1_path, folder2_path, output_folder_path, idx)
        print(f'{name} done')
