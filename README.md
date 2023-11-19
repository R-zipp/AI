# R-ZIPP (AI part)

메타버스 아카데미 2기 최종 프로젝트

# 프로젝트 소개

도면을 업로드 하여 3D 그래픽으로 구현해 원하는 물품들을 원하는 위치에 가상으로 배치할 수 있는 인테리어 서비스

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

## Blueprint to 3D
도면을 분석하여 벽과 방을 탐지하고 Blender script를 사용하여 3D파일로 변환

| ![image_0010](https://github.com/R-zipp/AI/assets/141614581/ef84f9ae-6b0e-42ca-881a-53ef8d7ec8e3) | ![제목 없음4](https://github.com/R-zipp/AI/assets/141614581/7cabb43b-fb10-4250-8466-b4c671c416a5) |
| :---: | :---: |
| 원본 도면 | 3D file |


- ### Detect walls and rooms
  
인식률 개선을 위하여 원본 도면을 이진화하고 벽, 방 탐지
  
| ![image_0018](https://github.com/R-zipp/AI/assets/141614581/dd3706a7-859e-4f44-9b70-038c3adff6f1) | ![image_0016](https://github.com/R-zipp/AI/assets/141614581/513bf31a-eddd-44a3-a2b0-3253bb77a5f3) | ![image_0017](https://github.com/R-zipp/AI/assets/141614581/0199fd06-78c7-4614-83b9-343b559cdaab) |
| :---: | :---: | :---: |
| Make binary | Walls | Rooms |

- ### OCR

  글자를 벽으로 인식하는 경우가 있어서 [EasyOCR](https://github.com/JaidedAI/EasyOCR)을 이용하여 제거

### Hand drawing to Blueprint
