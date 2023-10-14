from PIL import Image

# 이미지 경로 지정
example_img_path = 'Images/Examples/example.png'
test_img_path = 'Images/Test_img/Test_img1.jpg'

# 이미지 열기
example_image = Image.open(example_img_path)
test_image = Image.open(test_img_path)


print(example_image)
print(test_image)

bw_image = test_image.convert('L')

# PNG로 저장하기
bw_image.save('Images/Test_img/Test_img1_grayscale.jpg', "PNG")
# 이미지 표시
# image.show()
