from fastapi import FastAPI, UploadFile, HTTPException, File
from pydantic import BaseModel

import shutil
from pathlib import Path
import os
import time

from blueprint_to3D import BLueprintTo3D

app = FastAPI()
bLueprint_to_3D = BLueprintTo3D()


class Item(BaseModel):
    ImagePath: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/blueprint_to_3D")
async def create_user(item: Item):
    img_path = item.ImagePath
    img_path = '../AR-zipp/'+img_path.replace('\\', '/')

    img_name, extension = os.path.splitext(img_path.split('/')[-1])
    output_path = f'../AR-zipp/statics/blend_file/{img_name}.blend'

    project_path = bLueprint_to_3D.make_blend(img_path)
    shutil.copy(project_path, output_path)

    print('')
    print(f'File copied at : {output_path}')

    return f'{img_name}.blend'


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile = File(...)):
#     # 업로드된 파일의 확장자 확인
#     if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
#         raise HTTPException(status_code=400, detail="Invalid file format!")

#     try:
#         # 저장할 경로 설정
#         file_path = Path(f"uploads/{file.filename}")

#         # 파일 저장을 위한 준비
#         with file_path.open("wb") as buffer:
#             # 파일의 내용을 저장할 위치로 복사
#             shutil.copyfileobj(file.file, buffer)

#     finally:
#         # 파일 닫기
#         file.file.close()

#     return {"filename": file.filename}