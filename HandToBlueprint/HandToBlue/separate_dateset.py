import os
import shutil
from sklearn.model_selection import train_test_split

# 데이터셋이 위치한 기본 폴더
data_dir = 'stable_diffusion_1024_v0'

# 이미지 파일들의 리스트를 가져옵니다.
file_list = os.listdir(data_dir)

# 파일명을 기반으로 학습, 검증, 테스트 세트로 분리합니다.
# 여기서는 학습:검증:테스트 = 70:15:15 비율로 분리하도록 설정합니다.
train_files, test_files = train_test_split(file_list, test_size=0.3, random_state=42)
val_files, test_files = train_test_split(test_files, test_size=0.5, random_state=42)

# 결과적으로 다음과 같은 구조를 가지게 됩니다.
# dataset/
#   train/
#   val/
#   test/

# 학습, 검증, 테스트 폴더를 생성합니다.
for folder in ['train', 'val', 'test']:
    os.makedirs(os.path.join(data_dir, folder), exist_ok=True)

# 파일을 해당 폴더로 이동시킵니다.
def move_files(file_list, source_dir, target_dir):
    for file_name in file_list:
        shutil.move(os.path.join(source_dir, file_name),
                    os.path.join(target_dir, file_name))

# 파일을 각각의 폴더로 이동합니다.
move_files(train_files, data_dir, os.path.join(data_dir, 'train'))
move_files(val_files, data_dir, os.path.join(data_dir, 'val'))
move_files(test_files, data_dir, os.path.join(data_dir, 'test'))

print("Files are split into train, validation, and test folders.")
