import torchvision.transforms as transforms
import torch.nn.functional as F
from PIL import Image
import torch
import torch.nn as nn
import os
import numpy as np


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class Mish(nn.Module):
    def __init__(self):
        super(Mish, self).__init__()

    def forward(self, x):
        return x * torch.tanh(F.softplus(x))


class MultiHeadAttention(nn.Module):
    def __init__(self, in_dim, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.dim_per_head = in_dim // num_heads

        self.query_convs = nn.ModuleList([nn.Conv2d(in_dim, self.dim_per_head, kernel_size=1) for _ in range(num_heads)])
        self.key_convs = nn.ModuleList([nn.Conv2d(in_dim, self.dim_per_head, kernel_size=1) for _ in range(num_heads)])
        self.value_convs = nn.ModuleList([nn.Conv2d(in_dim, self.dim_per_head, kernel_size=1) for _ in range(num_heads)])

        self.softmax = nn.Softmax(dim=-1)
        self.output_conv = nn.Conv2d(in_dim, in_dim, kernel_size=1)


    def forward(self, x):
        batch_size, _, width, height = x.size()
        heads = []

        for i in range(self.num_heads):
            proj_query = self.query_convs[i](x).view(batch_size, -1, width * height).permute(0, 2, 1)
            proj_key = self.key_convs[i](x).view(batch_size, -1, width * height)
            proj_value = self.value_convs[i](x).view(batch_size, -1, width * height)

            energy = torch.bmm(proj_query, proj_key)
            attention = self.softmax(energy)
            head = torch.bmm(proj_value, attention.permute(0, 2, 1))
            heads.append(head.view(batch_size, self.dim_per_head, width, height))

        multi_head = torch.cat(heads, dim=1)
        output = self.output_conv(multi_head)
        return output


class SelfAttention(nn.Module):
    """ Self attention Layer"""
    def __init__(self, in_dim):
        super(SelfAttention,self).__init__()
        self.chanel_in = in_dim
        self.query_conv = nn.Conv2d(in_channels = in_dim , out_channels = in_dim//8 , kernel_size= 1)
        self.key_conv = nn.Conv2d(in_channels = in_dim , out_channels = in_dim//8 , kernel_size= 1)
        self.value_conv = nn.Conv2d(in_channels = in_dim , out_channels = in_dim , kernel_size= 1)
        self.gamma = nn.Parameter(torch.zeros(1))
        self.softmax = nn.Softmax(dim=-1)


    def forward(self,x):
        m_batchsize, C, width, height = x.size()
        proj_query = self.query_conv(x).view(m_batchsize, -1, width*height).permute(0, 2, 1)
        proj_key = self.key_conv(x).view(m_batchsize, -1, width*height)
        energy = torch.bmm(proj_query, proj_key)
        attention = self.softmax(energy)
        proj_value = self.value_conv(x).view(m_batchsize, -1, width*height)

        out = torch.bmm(proj_value, attention.permute(0, 2, 1))
        out = out.view(m_batchsize, C, width, height)

        out = self.gamma*out + x
        return out


class UNetDown(nn.Module):
    def __init__(self, in_channels, out_channels, normalize=True, dropout=0.0, use_attention=False, num_heads=8):
        super(UNetDown, self).__init__()
        layers = [nn.Conv2d(in_channels, out_channels, kernel_size=4, stride=2, padding=1, bias=False)]
        if use_attention:
            layers.append(SelfAttention(out_channels))
            self.attention = MultiHeadAttention(out_channels, num_heads)
        else:
            self.attention = None
        if normalize:
            layers.append(nn.InstanceNorm2d(out_channels))
        # layers.append(nn.LeakyReLU(0.2))
        layers.append(Mish())

        if dropout:
            layers.append(nn.Dropout(dropout))
        self.model = nn.Sequential(*layers)


    def forward(self, x):
        x = self.model(x)
        if self.attention:
            x = self.attention(x)
        return x


class UNetUp(nn.Module):
    def __init__(self, in_channels, out_channels, dropout=0.0):
        super(UNetUp, self).__init__()
        layers = [nn.ConvTranspose2d(in_channels, out_channels, kernel_size=4, stride=2, padding=1, bias=False)]
        layers.append(nn.InstanceNorm2d(out_channels))
        # layers.append(nn.ReLU(inplace=True))
        layers.append(Mish())

        if dropout:
            layers.append(nn.Dropout(dropout))
        self.model = nn.Sequential(*layers)


    def forward(self, x, skip_input):
        x = self.model(x)
        x = torch.cat((x, skip_input), 1)

        return x


class GeneratorUNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=3):
        super(GeneratorUNet, self).__init__()

        self.down1 = UNetDown(in_channels, 64, normalize=False) 

        self.down2 = UNetDown(64, 128) 
        self.down3 = UNetDown(128, 256)
        self.down4 = UNetDown(256, 512, dropout=0.5, use_attention=True, num_heads=8)
        self.down5 = UNetDown(512, 512, dropout=0.5, use_attention=True, num_heads=8)
        self.down6_extra = UNetDown(512, 512, dropout=0.5, use_attention=True, num_heads=8) 
        self.down6 = UNetDown(512, 512, dropout=0.5, use_attention=True, num_heads=8) 
        self.down7 = UNetDown(512, 512, dropout=0.5, use_attention=True, num_heads=8)
        self.down8 = UNetDown(512, 512, dropout=0.5, use_attention=True, num_heads=8)
        self.down9 = UNetDown(512, 512, normalize=False, dropout=0.5)

        self.up1 = UNetUp(512, 512, dropout=0.5)
        self.up2 = UNetUp(1024, 512, dropout=0.5) 
        self.up3 = UNetUp(1024, 512, dropout=0.5) 
        self.up4 = UNetUp(1024, 512, dropout=0.5) 
        self.up5 = UNetUp(1024, 512, dropout=0.5)
        self.up5_extra = UNetUp(1024, 512, dropout=0.5) 
        self.up6 = UNetUp(1024, 256)
        self.up7 = UNetUp(512, 128) 
        self.up8 = UNetUp(256, 64)

        self.final = nn.Sequential(
            nn.Upsample(scale_factor=2),
            nn.ZeroPad2d((1, 0, 1, 0)),
            nn.Conv2d(128, out_channels, kernel_size=4, padding=1), 
            nn.Tanh(),
        )

    def forward(self, x):
        d1 = self.down1(x)
        d2 = self.down2(d1)
        d3 = self.down3(d2)
        d4 = self.down4(d3)
        d5 = self.down5(d4)
        d6 = self.down6(d5)
        d6_extra = self.down6_extra(d6)
        d7 = self.down7(d6_extra)
        d8 = self.down8(d7)
        d9 = self.down9(d8)
        u1 = self.up1(d9, d8)
        u2 = self.up2(u1, d7)
        u3 = self.up3(u2, d6_extra)
        u4 = self.up4(u3, d6)
        u5 = self.up5(u4, d5)
        u5_extra = self.up5_extra(u5, d4)
        u6 = self.up6(u5_extra, d3)
        u7 = self.up7(u6, d2)
        u8 = self.up8(u7, d1)

        return self.final(u8)


class BlueprintGenerator():
    def __init__(self, model_path):
        self.generator = GeneratorUNet()
        # self.generator.cuda()
        self.generator.to(device)

        self.generator.load_state_dict(torch.load(model_path, map_location=device))
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
        image = transform(image).unsqueeze(0).to(device)

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


    def image_save(self, file, image, add_origin=False, output_dir='./output', name='gen_img'):
        os.makedirs(output_dir, exist_ok=True)
        name, extension = os.path.splitext(name)
        
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
                
            extention = '.png' if extension == '' else extension
            output_path = os.path.join(output_dir, name+extention)
            image.save(output_path)
            
        else:
            raise Exception('File type is not correct!')
        
        print(f'>> Save image : {output_path}')
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
            save_path = self.image_save(file, generated_image, add_origin=self.add_origin, output_dir=self.output_dir, name=self.output_name)
        
            return save_path, generated_image
        else:
            return None, generated_image
                

    def parameter_setting(self, want_img='all', add_origin=False, output_dir='./output', new_width=1024, output_name='gen_img'):
        self.add_origin = add_origin
        self.output_dir = output_dir
        self.want_img = want_img
        self.output_name = output_name
        self.new_width = new_width
        
        
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
    model_path = "./Resources/models/G_best_size1024.pt"
    # model_path = "./models/Best_saved_models/G_best_size1024.pt"
    # model_path = "./models/saved_models_each_50epoch/G_size1024_350.pt"
    generator = BlueprintGenerator(model_path)

    directory = 'Statics/images/SD_output_2/cycle_6'
    file = 'Statics/images/SD_output_2/cycle_1/image_1014_(01).png'
    
    image = Image.open(file)
    
    # generator.data_load(file=file)
    # generator.data_load(directory=directory)
    # generator.data_load(image=image)
    # generator.parameter_setting(
    #                             want_img='all', 
    #                             add_origin=True, 
    #                             output_dir='./output_2')
    # result_img = generator.run(save=True)
    
    generator.data_load(directory=directory)
    generator.parameter_setting(
                            want_img='all', 
                            add_origin=True, 
                            output_dir='./statics/generate_img')
    generating_result, result_img = generator.run(save=True)