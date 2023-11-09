from PIL import Image
import os

test_dir = 'stable_diffusion_1108_v0/test'
img_list = os.listdir(test_dir)

for img_name in img_list[:]:
    original_image_path = os.path.join(test_dir, img_name)
    image = Image.open(original_image_path)

    # 이미지의 크기를 구합니다
    width, height = image.size

    # 이미지를 가로로 반으로 나눕니다
    left_image = image.crop((0, 0, width//2, height))
    right_image = image.crop((width//2, 0, width, height))

    output_dir = 'test_origin'
    os.makedirs(output_dir, exist_ok=True)

    # left_image_path = 'left_image.jpg'
    # left_image.save(os.path.join(output_dir, left_image_path))

    right_image_path = f'{img_name}'
    right_image.save(os.path.join(output_dir, right_image_path))
