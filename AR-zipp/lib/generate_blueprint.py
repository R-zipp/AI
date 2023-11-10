import torchvision.transforms as transforms
from torchvision.utils import save_image
from PIL import Image
import torch
import torch.nn as nn
import os
import numpy as np



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


class BlueprintGenerator():
    def __init__(self, model_path):
        self.generator = GeneratorUNet()
        self.generator.cuda()

        self.generator.load_state_dict(torch.load(model_path))
        self.generator.eval()
        
        self.data = None

    
    def generate_image(self, image, want_img='all'):
        width, height = image.size
        
        if want_img == 'all':
            image = image.copy()
        elif want_img == 'left':
            left_half = image.crop((0, 0, width//2, height))
            image = left_half.copy()
        elif want_img == 'right':
            right_half = image.crop((width//2, 0, width, height))
            image = right_half.copy()
        else:
            raise Exception('mode is not correct')
        
        num_channels = len(image.getbands())

        # If the image is grayscale
        if num_channels == 1:
            image = image.convert('RGB')

        # If the image is RGBA
        elif num_channels == 4:
            image = image.convert('RGB')

        # If the image is RGB
        elif num_channels == 3:
            image = image

        transform = transforms.Compose([
            transforms.Resize((1024, 1024), Image.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        image = transform(image).unsqueeze(0).cuda()

        with torch.no_grad():
            generated_image = self.generator(image)

        generated_image = (generated_image + 1) / 2 
        
        # tensor to array
        tensor = generated_image.squeeze(0)
        tensor = tensor.cpu()
        
        tensor = tensor.mul(255).clamp(0, 255).byte()
        numpy_array = tensor.numpy()
        numpy_array = np.transpose(numpy_array, (1, 2, 0))
        generated_image = Image.fromarray(numpy_array)

        return generated_image


    def image_save(self, file, image, add_origin=False, output_dir='./output', default_name='gen_img'):
        os.makedirs(output_dir, exist_ok=True)
        
        if type(file) is str: 
            name = file.split('/')[-1].split('\\')[-1]
            
            if add_origin:
                original_img = Image.open(file)
                width1, height1 = original_img.size
                width2, height2 = image.size

                new_width = width1 + width2
                new_height = max(height1, height2)

                new_image = Image.new('RGB', (new_width, new_height))

                new_image.paste(original_img, (0, 0))
                new_image.paste(image, (width1, 0))
                image = new_image.copy()

            output_path = os.path.join(output_dir, name)
            image.save(output_path)
        
        elif isinstance(file, Image.Image):
            if add_origin:
                original_img = file.copy()
                width1, height1 = original_img.size
                width2, height2 = image.size

                new_width = width1 + width2
                new_height = max(height1, height2)

                new_image = Image.new('RGB', (new_width, new_height))

                new_image.paste(original_img, (0, 0))
                new_image.paste(image, (width1, 0))
                image = new_image.copy()
                
            extention = '.png'
            output_path = os.path.join(output_dir, default_name+extention)
            image.save(output_path)
            
        else:
            raise Exception('File type is not correct!')
            
        return output_path


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
            
            
    def process(self, file, save):
        if isinstance(file, Image.Image):
            image = file.copy()
        else:
            image = Image.open(file)
            
        generated_image = self.generate_image(image, want_img=self.want_img)
        
        if save:
            save_path = self.image_save(file, generated_image, add_origin=self.add_origin, output_dir=self.output_dir, default_name='gen_img')
        
            return save_path, generated_image
        else:
            return None, generated_image
                

    def parameter_setting(self, want_img='all', add_origin=False, output_dir='./output'):
        self.add_origin = add_origin
        self.output_dir = output_dir
        self.want_img = want_img
        
        
    def run(self, save=False):
        if type(self.data) is str:
            file = self.data
            generated_image = self.process(file, save=save)
            
        elif type(self.data) is list:
            for file in self.data[:]:
                save_path, generated_image = self.process(file, save=save)
                
        elif isinstance(self.data, Image.Image):
            file = self.data
            save_path, generated_image = self.process(file, save=save)
                
        print('Blueprint generate done')
        return save_path, generated_image



if __name__ == '__main__':
    model_path = "./models/G_no_ocr_binary_size1024_1109.pt"
    generator = BlueprintGenerator(model_path)

    directory = 'statics/Images/cycle_6'
    file = 'statics/Images/cycle_6/image_0_(06).png'
    
    image = Image.open(file)
    # image_array = np.array(image)
    
    # generator.data_load(file=file)
    generator.data_load(directory=directory)
    # generator.data_load(image=image)
    generator.parameter_setting(
                                want_img='all', 
                                add_origin=True, 
                                output_dir='./output_2')
    result_img = generator.run(save=True)