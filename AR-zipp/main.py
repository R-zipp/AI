from fastapi import FastAPI, Request, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import shutil
from pathlib import Path
import os
from datetime import datetime
import requests
import json

from lib.preprocessing import PreProcessing
from lib.blend_to_fbx import BlendToFBX


app = FastAPI()
preprocessing = PreProcessing()
converter = BlendToFBX()

app.mount("/statics", StaticFiles(directory="statics"), name="statics")



class Item(BaseModel):
    ImagePath: str

class Image_bi(BaseModel):
    ImagePath: str



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/fbx_file_list")
def read_root():
    fbx_files = [file for file in os.listdir('static/fbx_file') if file.endswith('.fbx')]
    return {"fbx_list": fbx_files}


@app.post("/test_api/in_json_out_str")
async def create_user(item: Item):
    now = datetime.now()
    print('')
    print(f'in_json_out_str / {now} / {item.ImagePath}')
    print('')
    return item.ImagePath


@app.post("/test_api/in_json_out_json")
async def create_user(item: Item):
    return_json = {
        'ImagePath' : item.ImagePath
    }
    now = datetime.now()
    print('')
    print(f'in_json_out_json / {now}')
    print('')
    return JSONResponse(content=return_json)


@app.post("/test_api/in_img_out_json")
async def upload_image(request: Request):
    content_type = request.headers.get('content-type')
    if content_type != 'image/jpeg':
        raise HTTPException(status_code=400, detail="Content-Type is not image/jpeg")

    body = await request.body()

    try:
        # 이미지 파일 저장할 경로 지정 (예: 현재 작업 디렉토리 아래의 'uploads' 폴더)
        upload_folder = Path(os.getcwd()) / "uploads"
        upload_folder.mkdir(parents=True, exist_ok=True)

        # # 파일 경로 생성
        file_path = upload_folder / "uploaded_image.jpg"

        with open(file_path, "wb") as image_file:
            image_file.write(body)
        
        return JSONResponse(content={"message": "Image uploaded successfully", "filename": 'file_path.name'}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    # 업로드된 파일의 확장자 확인
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Invalid file format!")

    try:
        file_dir = f"statics/Images/uploads/"
        storage_path = Path(file_dir)
        if not os.path.exists(storage_path):
            storage_path.mkdir(parents=True, exist_ok=True)

        file_path = storage_path / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Preprocessing
        ouput_path = 'statics/Images/After_preprocessing'
        preprocessing.run(str(file_path), ouput_path)
        preprocessing_result = preprocessing.file_save_path('OCR')
        print(preprocessing_result)

        # Image to blend file
        url = 'http://127.0.0.1:8001/blueprint_to_3D'

        data = {'ImagePath': preprocessing_result}

        response = requests.post(url, json=data)
        print('Status Code:', response.status_code)
        print('Response Content:', response.text)

        # Blend to fbx converter
        blend_name = response.text.replace('"','')
        blend_path = f"statics/blend_file/{blend_name}"
        print(blend_path)
        fbx_dir = 'statics/fbx_file'
        converter.blend_to_fbx(blend_path, fbx_dir)

    finally:
        file.file.close()

    return {"filename": fbx_dir}