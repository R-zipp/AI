import subprocess
import os

# Blender에서 실행할 Python 스크립트 파일 경로
blender_script = './lib/fbx_converter.py'

os.environ['BLEND_PATH'] = './statics/blend_file/7b9dfc68-44ab-42c9-803c-834fd38d6bb0.blend'

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
