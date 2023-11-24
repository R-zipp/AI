# Python 3.8 베이스 이미지 사용
FROM python:3.8

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 파일들을 컨테이너의 /app에 복사
COPY . .

# 필요한 Python 패키지 설치
RUN pip install -r requirements.txt

# Blender 설치를 위한 필요 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    libx11-dev \
    libxxf86vm-dev \
    libxcursor-dev \
    libxi-dev \
    libxrandr-dev \
    libxinerama-dev \
    libglew-dev

# Blender 다운로드 및 압축 해제
RUN wget https://download.blender.org/release/Blender3.6/blender-3.6.4-linux-x64.tar.xz \
    && tar -xf blender-3.6.4-linux64.tar.xz -C /usr/local \
    && rm blender-3.6.4-linux64.tar.xz

# Blender 실행 파일의 경로를 환경변수 PATH에 추가
ENV PATH="/usr/local/blender-3.6.4-linux64:${PATH}"

# FastAPI 애플리케이션 실행
CMD uvicorn --host=0.0.0.0 --port 8000 main:app
