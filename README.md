# R-ZIPP (AI part)

메타버스 아카데미 2기 최종 프로젝트

# 프로젝트 소개

도면을 업로드 하여 3D 그래픽으로 구현해 원하는 물품들을 원하는 위치에 가상으로 배치할 수 있는 인테리어 서비스

AI기술을 활용하여 사용자가 도면을 입력하면 3D 파일(fbx, glb 등)로 결과를 반환

모든 사람이 집 도면을 구할 수 없고 실제 있는 집이 아니라 가상의 집을 만들 수 있도록 손으로 그린 도면 그림을 이용하여 도면을 생성하는 기능을 추가하였음

# 팀원 소개 및 역할

| AI | AI | server | Unreal | Unreal | Data science |
|:--:|:--:|:------:|:------:|:------:|:------------:|
| 정민교 | 김종민 | 김나영 | 김채린 | 반재형 | 강지석 |

#### AI 세부 역할 분담
- 정민교
1. Blueprint to 3D를 활용하여 도면을 3D fbx파일로 변환
2. FastAPI를 활용하여 모델 서빙

- 김종민
1. 손그림 학습을 위해 Stable Diffusion을 사용하여 데이터 셋 제작
2. Hand drawting to Blueprint 모델 학습

# 주요 기술

### Blueprint to 3D
도면을 분석하여 벽과 방을 탐지하고 Blender script를 사용하여 3D파일로 변환

| ![image_0010](https://github.com/R-zipp/AI/assets/141614581/ef84f9ae-6b0e-42ca-881a-53ef8d7ec8e3) | ![제목 없음4](https://github.com/R-zipp/AI/assets/141614581/7cabb43b-fb10-4250-8466-b4c671c416a5) |
| :---: | :---: |
| 원본 도면 | 3D file |


- #### Detect walls and rooms

  인식률 개선을 위하여 원본 도면을 이진화하고 벽, 방 탐지
  
  | ![image_0018](https://github.com/R-zipp/AI/assets/141614581/dd3706a7-859e-4f44-9b70-038c3adff6f1) | ![image_0016](https://github.com/R-zipp/AI/assets/141614581/513bf31a-eddd-44a3-a2b0-3253bb77a5f3) | ![image_0017](https://github.com/R-zipp/AI/assets/141614581/0199fd06-78c7-4614-83b9-343b559cdaab) |
  | :---: | :---: | :---: |
  | Make binary | Walls | Rooms |

- #### OCR

  글자를 벽으로 인식하는 경우가 있어서 [EasyOCR](https://github.com/JaidedAI/EasyOCR)을 이용하여 제거

- #### bpy

  python을 사용한 Blender script 라이브러리. python에서 직접 사용도 가능하지만 불안정한 부분이 많아 추천하지 않는다. subprocess로 Blender를 실행시키고 거기서 script파일을 실행시키는 방법을 추천.

        blender_script = 'Lib/fbx_converter.py'

        os.environ['BLEND_PATH'] = blend_path
        os.environ['SIZE_MULTIPLIER'] = str(size_multiplier)
        
        blender_command = [
                            'C:/Program Files/Blender Foundation/Blender 3.6/blender.exe',
                            '-b',
                            '--python', blender_script
                            ]
        
        process = subprocess.run(blender_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

### Hand drawing to Blueprint

- #### Data set

  1) **도면 이미지 수집**
     
     AI Hub의 [건축 도면 데이터](https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=realm&dataSetSn=71465) 약 48000장 중에 명확하게 벽과 문과 창문을 구분 할 수 있는 이미지 1000장을 골라냄

      테스트 용으로 사용하던 네이버 부동산에서 크롤링한 도면 데이터 200장을 합쳐 약 1200장의 도면 데이터 확보

  | ![그림1 (1)](https://github.com/R-zipp/AI/assets/141614581/b2ece517-bc94-4fec-90d9-dde000efe4f5) | ![APT_CS_OCR_026313215 (1)](https://github.com/R-zipp/AI/assets/141614581/5a22ceda-968e-436e-b151-3d087503eb40) | ![APT_FP_OBJ_009064152 (1)](https://github.com/R-zipp/AI/assets/141614581/ef7f735b-4de0-427a-a410-a90c47170106) |
  | :---: | :---: | :---: |
  | 구분하기 어려운 도면 | 측면 도면 | 사용 가능한 도면 |

     
  2) **Stable Diffusion을 이용한 데이터 셋 제작**
 
     모든 도면에 대한 손 그림을 직접 그릴 수 없어 Stable Diffusion Cany 모델을 활용하여 도면의 모양을 유지하며 손으로 그린 듯한 이미지를 생성
     
  | ![그림2](https://github.com/R-zipp/AI/assets/141614581/ca5b812c-7d68-43fc-8fa0-32d54981b900) | ![그림3](https://github.com/R-zipp/AI/assets/141614581/3fee87a2-1c7c-4dff-8250-0fe637e071fc) | ![그림4](https://github.com/R-zipp/AI/assets/141614581/59abaa6e-bdfd-4a02-948d-984a49477bcb) | ![그림5](https://github.com/R-zipp/AI/assets/141614581/b387252c-e904-4d8c-848d-385d01657cac) |
  | :---: | :---: | :---: | :---: |
  | 원본 이미지 | Generated img1 | Generated img2 | Generated img1 |

- #### Model train

  pix2pix 모델을 이용하여 손 도면을 도면과 같은 형태로 이미지 생성

  | :---: | :---: | :---: | :---: |

### 결과



# 기술 스택

### - 언어
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">

### - 주요 라이브러리
 <img src="https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white"> <img src="https://img.shields.io/badge/pytorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white"> <img src="https://img.shields.io/badge/opencv-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white">

### - 개발 툴
<img src="https://img.shields.io/badge/VS code-2F80ED?style=for-the-badge&logo=VS code&logoColor=white"> <img src="https://img.shields.io/badge/Google Colab-F9AB00?style=for-the-badge&logo=Google Colab&logoColor=white">

### - 협업 툴
<img src="https://img.shields.io/badge/Github-181717?style=for-the-badge&logo=Github&logoColor=white"> <img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=Notion&logoColor=white">

# 참고자료
