from flask import Flask, request, jsonify
import os

import glob
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import torch
import torch.nn as nn

from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from torchvision.utils import save_image


# U-Net 아키텍처의 다운 샘플링(Down Sampling) 모듈
class UNetDown(nn.Module):
    def __init__(self, in_channels, out_channels, normalize=True, dropout=0.0):
        super(UNetDown, self).__init__()
        # 너비와 높이가 2배씩 감소
        layers = [nn.Conv2d(in_channels, out_channels, kernel_size=4, stride=2, padding=1, bias=False)]
        if normalize:
            layers.append(nn.InstanceNorm2d(out_channels))
        layers.append(nn.LeakyReLU(0.2))
        if dropout:
            layers.append(nn.Dropout(dropout))
        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)

# U-Net 아키텍처의 업 샘플링(Up Sampling) 모듈: Skip Connection 사용
class UNetUp(nn.Module):
    def __init__(self, in_channels, out_channels, dropout=0.0):
        super(UNetUp, self).__init__()
        # 너비와 높이가 2배씩 증가
        layers = [nn.ConvTranspose2d(in_channels, out_channels, kernel_size=4, stride=2, padding=1, bias=False)]
        layers.append(nn.InstanceNorm2d(out_channels))
        layers.append(nn.ReLU(inplace=True))
        if dropout:
            layers.append(nn.Dropout(dropout))
        self.model = nn.Sequential(*layers)

    def forward(self, x, skip_input):
        x = self.model(x)
        x = torch.cat((x, skip_input), 1) # 채널 레벨에서 합치기(concatenation)

        return x

# U-Net 생성자(Generator) 아키텍처
class GeneratorUNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=3):
        super(GeneratorUNet, self).__init__()

        self.down1 = UNetDown(in_channels, 64, normalize=False) # 출력: [64 X 128 X 128]
        self.down2 = UNetDown(64, 128) # 출력: [128 X 64 X 64]
        self.down3 = UNetDown(128, 256) # 출력: [256 X 32 X 32]
        self.down4 = UNetDown(256, 512, dropout=0.5) # 출력: [512 X 16 X 16]
        self.down5 = UNetDown(512, 512, dropout=0.5) # 출력: [512 X 8 X 8]
        self.down6 = UNetDown(512, 512, dropout=0.5) # 출력: [512 X 4 X 4]
        self.down7 = UNetDown(512, 512, dropout=0.5) # 출력: [512 X 2 X 2]
        self.down8 = UNetDown(512, 512, normalize=False, dropout=0.5) # 출력: [512 X 1 X 1]

        # Skip Connection 사용(출력 채널의 크기 X 2 == 다음 입력 채널의 크기)
        self.up1 = UNetUp(512, 512, dropout=0.5) # 출력: [1024 X 2 X 2]
        self.up2 = UNetUp(1024, 512, dropout=0.5) # 출력: [1024 X 4 X 4]
        self.up3 = UNetUp(1024, 512, dropout=0.5) # 출력: [1024 X 8 X 8]
        self.up4 = UNetUp(1024, 512, dropout=0.5) # 출력: [1024 X 16 X 16]
        self.up5 = UNetUp(1024, 256) # 출력: [512 X 32 X 32]
        self.up6 = UNetUp(512, 128) # 출력: [256 X 64 X 64]
        self.up7 = UNetUp(256, 64) # 출력: [128 X 128 X 128]

        self.final = nn.Sequential(
            nn.Upsample(scale_factor=2), # 출력: [128 X 256 X 256]
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(128, out_channels, kernel_size=4, padding=1), # 출력: [3 X 256 X 256]
            nn.Tanh(),
        )

    def forward(self, x):
        # 인코더부터 디코더까지 순전파하는 U-Net 생성자(Generator)
        d1 = self.down1(x)
        d2 = self.down2(d1)
        d3 = self.down3(d2)
        d4 = self.down4(d3)
        d5 = self.down5(d4)
        d6 = self.down6(d5)
        d7 = self.down7(d6)
        d8 = self.down8(d7)
        u1 = self.up1(d8, d7)
        u2 = self.up2(u1, d6)
        u3 = self.up3(u2, d5)
        u4 = self.up4(u3, d4)
        u5 = self.up5(u4, d3)
        u6 = self.up6(u5, d2)
        u7 = self.up7(u6, d1)

        return self.final(u7)


def generate_image(input_path, output_path, model_path):
    generator = GeneratorUNet()
    generator.cuda()

    # 모델의 가중치를 불러옵니다.
    generator.load_state_dict(torch.load(model_path))
    generator.eval()  # 평가 모드로 변경합니다.

    # 입력 이미지를 불러옵니다.
    image = Image.open(input_path)


    # 이미지의 채널 수를 확인합니다.
    num_channels = len(image.getbands())

    # 이미지가 그레이스케일인 경우
    if num_channels == 1:
        image = image.convert('RGB')

    # 이미지가 RGBA인 경우
    elif num_channels == 4:
        image = image.convert('RGB')

    # 이미지가 이미 RGB인 경우
    elif num_channels == 3:
        image = image


    # 이미지 변환(transform)을 적용합니다.
    transform = transforms.Compose([
        transforms.Resize((1024, 1024), Image.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    image = transform(image).unsqueeze(0).cuda()  # 배치 차원을 추가하고 GPU에 올립니다.

    # 이미지를 생성합니다.
    with torch.no_grad():
        generated_image = generator(image)

    # 생성된 이미지를 저장하기 위해 처리합니다.
    generated_image = (generated_image + 1) / 2  # [-1, 1] 범위를 [0, 1] 범위로 변경합니다.
    save_image(generated_image, output_path)

# 함수 호출
# generate_image("./infe/APT_FP_OBJ_997579028.jpg", "./infe/Answer_222.jpg", "Pix2Pix_Generator_size1024_1028.pt")


app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    # request에서 json 데이터를 가져옵니다.
    data = request.get_json()
    input_path = data['input_path']
    output_path = data['output_path']
    model_path = data['model_path']

    # generate_image 함수를 호출하여 이미지를 생성합니다.
    try:
        generate_image(input_path, output_path, model_path)
        return jsonify({'message': 'Image generated successfully', 'output_path': output_path}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
