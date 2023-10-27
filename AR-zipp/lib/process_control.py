import subprocess
import os

def execute_blender_script(blend_file, fbx_dir):
    # Blender가 설치된 경로. 이 경로는 시스템에 따라 다를 수 있습니다.
    blender_executable_path = "/path/to/blender"

    # 실행할 스크립트의 경로
    script_path = "/path/to/blend_to_fbx.py"  # 앞서 만든 스크립트 파일의 위치를 지정해주세요.

    # subprocess를 사용하여 Blender 실행 및 스크립트 호출
    process = subprocess.Popen(
        [
            blender_executable_path,
            "--background",  # 백그라운드에서 Blender를 실행합니다.
            "--python", script_path,  # Python 스크립트 실행
            "--",  # 이후의 인수는 스크립트에 전달됩니다.
            blend_file,
            fbx_dir,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 스크립트 출력을 캡처하고 출력
    output, error = process.communicate()

    if process.returncode != 0:
        print(f"Error occurred: {error.decode()}")
    else:
        print(f"Output: {output.decode()}")

    # Blender 프로세스가 종료되었는지 확인
    return process.returncode

# 이 함수를 사용하여 스크립트 실행
blend_file_path = "/path/to/your/file.blend"  # 변환할 .blend 파일의 경로
export_directory = "/path/where/you/want/to/export/fbx"  # 내보낼 fbx 파일의 디렉토리

return_code = execute_blender_script(blend_file_path, export_directory)
if return_code == 0:
    print("Blender script executed successfully.")
else:
    print("An error occurred during the execution.")
