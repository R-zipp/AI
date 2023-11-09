import os

    
def file_remove_idex(input_dir, idx):
    file_list = os.listdir(input_dir)

    for name in file_list[:]:
        old_name = os.path.join(input_dir, name)
        
        new = name.replace(f'_(0{idx})', '')
        new_name = os.path.join(input_dir, new)
        os.rename(old_name, new_name)
    
    
def file_rename(input_dir):
    file_list = os.listdir(input_dir)

    for name in file_list[:3]:
        old_name = os.path.join(input_dir, name)
        
        new = int(name.split('_')[-1].split('.')[0])
        new_name = f'image_{new:04d}.png'
        print(new_name)
        # new = name.replace('_(04)', '')
        # new_name = os.path.join(input_dir, new)
        # os.rename(old_name, new_name)

    

if __name__ == '__main__':
    data_list = ['cycle_0', 'cycle_1', 'cycle_2', 'cycle_3', 'cycle_4']
    # data_list = ['cycle_1', 'cycle_2', 'cycle_3', 'cycle_4']
    
    for idx, name in enumerate(data_list):
        input_dir = f'./stable_diffusion/{name}'
        file_remove_idex(input_dir, idx)
        # file_rename(input_dir)