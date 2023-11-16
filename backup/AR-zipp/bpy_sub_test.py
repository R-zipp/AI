import subprocess
import os

# Blender에서 실행할 Python 스크립트 파일 경로
blender_script = './lib/fbx_converter.py'

os.environ['BLEND_PATH'] = './statics/blend_file/image_001.blend'
os.environ['SIZE_MULTIPLIER'] = str(3)


# Blender 실행 명령 구성
blender_command = [
    'C:/Program Files/Blender Foundation/Blender 3.6/blender.exe',      # Blender 실행 파일 경로
    '-b',           # 백그라운드 모드로 실행
    '--python', blender_script  # 실행할 Python 스크립트
]

# 서브프로세스 실행
process = subprocess.run(blender_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 결과 출력
print(process.stdout.decode())
print("STDERR:", process.stderr.decode())
