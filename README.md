# 🏠 R-집 : 도면 인식을 이용한 인테리어 플랫폼 (AI part)

메타버스 아카데미 2기 최종 프로젝트

#### 🎥 시연 영상 보러가기([Click](https://www.youtube.com/watch?v=5uSdEBHfxK4&ab_channel=minkyo))
#### 📙 발표자료 보러가기([Click](https://github.com/R-zipp/AI/blob/main/Docs/AR%EC%A7%91_%EC%A7%91%EC%97%90%EA%B0%88%EC%88%98%EC%9E%88%EB%82%98%EC%98%81_Beta.pdf))

<br/>

# :family: 팀원 소개 및 역할

**개발기간: 2023.10.07 ~ 2023.11.30**

| AI | AI | server | Unreal | Unreal | Data science |
|:--:|:--:|:------:|:------:|:------:|:------------:|
| 정민교 | 김종민 | 김나영 | 김채린 | 반재형 | 강지석 |

### AI 세부 역할 분담

<table>
    <tbody>
        <tr>
            <td><b>정민교</b></td>
            <td>Blueprint to 3D를 이용한 도면 3D 파일로 변환, FastAPI를 활용하여 모델 서빙</td>
        </tr>
        <tr>
            <td><b>김종민</b></td>
            <td>Stable Diffusion을 사용하여 데이터 셋 제작, Hand drawting to Blueprint 모델 학습</td>
        </tr>
    </tbody>
</table>

<br/>

# 🤝 융합 구조도

<br/>

# 💡 프로젝트 소개

**도면을 업로드 하여 3D 그래픽으로 구현해 원하는 물품들을 원하는 위치에 가상으로 배치할 수 있는 인테리어 서비스**

AI기술을 활용하여 사용자가 도면을 입력하면 3D 파일(fbx, glb 등)로 결과를 반환

모든 사람이 집 도면을 구할 수 없고 실제 있는 집이 아니라 가상의 집을 만들 수 있도록 손으로 그린 도면 그림을 이용하여 도면을 생성하는 기능을 추가하였음

<br/>

# :scroll: 주요 내용

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

  다만 텍스트가 세로로 되어있는 경우 인식율이 나쁘고 기울어져 있으면 인식이 불가능

  | ![image](https://github.com/R-zipp/AI/assets/141614581/c9ffc6e1-a6d6-4136-9b35-7e5f6b5d3bda) | ![image](https://github.com/R-zipp/AI/assets/141614581/f306fb0c-407e-49f8-8d73-a1550b589ebc) | ![image](https://github.com/R-zipp/AI/assets/141614581/dfe259fe-0273-41ed-82f6-74274582fc50) |
  | :---: | :---: | :---: |
  | 원본 도면 | OCR | Text remove |
  

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
     
     하나의 도면을 이용하여 여러 장의 이미지를 생성하여 데이터를 증강함
     
     최종 데이터 셋은 하나의 도면 당 10장의 이미지를 생성하여 약 12000장을 이용하여 학습
     
  | ![그림2](https://github.com/R-zipp/AI/assets/141614581/ca5b812c-7d68-43fc-8fa0-32d54981b900) | ![그림3](https://github.com/R-zipp/AI/assets/141614581/3fee87a2-1c7c-4dff-8250-0fe637e071fc) | ![그림4](https://github.com/R-zipp/AI/assets/141614581/59abaa6e-bdfd-4a02-948d-984a49477bcb) | ![그림5](https://github.com/R-zipp/AI/assets/141614581/b387252c-e904-4d8c-848d-385d01657cac) |
  | :---: | :---: | :---: | :---: |
  | 원본 이미지 | Generated img1 | Generated img2 | Generated img3 |

- #### Model train

  pix2pix 모델을 이용하여 손 도면을 도면과 같은 형태로 이미지 생성
  
  | ![0](https://github.com/R-zipp/AI/assets/141614581/6684026e-48b6-4e4f-8e7b-33e309562b41) | ![1000](https://github.com/R-zipp/AI/assets/141614581/3af64330-8269-4e27-b0b2-b9cee883c7da) | ![2000](https://github.com/R-zipp/AI/assets/141614581/d836a202-da8a-4ee7-9893-80880b88fafb) | ![3000](https://github.com/R-zipp/AI/assets/141614581/fcaabaca-19b2-4012-8f66-df4e9d40eaba) | ![4000](https://github.com/R-zipp/AI/assets/141614581/cfd7c2d6-dae3-4fda-bb0e-cda675d26d64) | ![47000](https://github.com/R-zipp/AI/assets/141614581/3bf1c84f-e643-4e83-ba59-7e8d7e7fb403) |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | Epoch1 | Epoch10 | Epoch30 | Epoch50 | Epoch100 | Epoch300 |

### 결과

  | ![그림1 (2)](https://github.com/R-zipp/AI/assets/141614581/265e36d8-119c-486d-88fa-6bc5527787d3) | ![그림2 (1)](https://github.com/R-zipp/AI/assets/141614581/2c4501a9-d54a-459a-9416-8fb37877759c) | ![ppt_1](https://github.com/R-zipp/AI/assets/141614581/5433c60d-f3e5-4a8f-8aa5-a5ae3e2f4ff2) |
  | :---: | :---: | :---: |
  | ![그림4 (1)](https://github.com/R-zipp/AI/assets/141614581/23acad0c-e3b1-4f08-9fe2-62c1e798138a) | ![그림5 (1)](https://github.com/R-zipp/AI/assets/141614581/81f0b640-a887-4a98-b580-13e102c30132) | ![ppt_2](https://github.com/R-zipp/AI/assets/141614581/ea7fb233-7db1-4889-a3fe-337c5d3e1f0e) |
  | Hand drawing image | Generated blueprint | 3D file |

<br/>

# 🛠 기술 스택

### - 언어
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">

### - 주요 라이브러리
 <img src="https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white"> <img src="https://img.shields.io/badge/pytorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white"> <img src="https://img.shields.io/badge/opencv-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white">

### - 개발 툴
<img src="https://img.shields.io/badge/VS code-2F80ED?style=for-the-badge&logo=VS code&logoColor=white"> <img src="https://img.shields.io/badge/Google Colab-F9AB00?style=for-the-badge&logo=Google Colab&logoColor=white">

### - 협업 툴
<img src="https://img.shields.io/badge/Github-181717?style=for-the-badge&logo=Github&logoColor=white"> <img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=Notion&logoColor=white">

# 🔍 참고자료

### Papers

1. [Isola, P., Zhu, J., Zhou, T., & Efros, A. A. (2017, November 22). Image-to-Image Translation with Conditional Adversarial Networks. Arxiv. https://arxiv.org/abs/1611.07004](https://arxiv.org/abs/1611.07004)

### GitHub

1. [pytorch-CycleGAN-and-pix2pix](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix)
2. [pytorch-hed](https://github.com/sniklaus/pytorch-hed)
3. [FloorplanToBlender3d](https://github.com/grebtsew/FloorplanToBlender3d)

### Blog

1. [[논문실습] Pix2Pix](https://velog.io/@wilko97/%EB%85%BC%EB%AC%B8%EC%8B%A4%EC%8A%B5-Pix2Pix)
2. [딥러닝 기반 건축도면 생성 모델 개발](https://brunch.co.kr/@ddkddk35/10)

<br/>

<br/>

---

special thanks to [정민](https://github.com/min731)
