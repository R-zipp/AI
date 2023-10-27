from fastapi import FastAPI, Request, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import shutil
from pathlib import Path
import os
from datetime import datetime
import requests
from urllib.parse import urlparse

from lib.preprocessing import PreProcessing
from lib.blend_to_fbx import BlendToFBX
from lib.image_to_fbx import ImageToFBX


app = FastAPI()
preprocessing = PreProcessing()
converter = BlendToFBX()
ItoFBX = ImageToFBX()

app.mount("/statics", StaticFiles(directory="statics"), name="statics")



class Item(BaseModel):
  drawingType: str
  userDrawingImage: str

class ImageReceive(BaseModel):
  drawingType: str
  userDrawingImage: str

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
    now = datetime.now()
    print('')
    print(f'in_json_out_json / {now} / {item.userDrawingImage}')
    print('')

    response = requests.get(item.userDrawingImage, stream=True)
    if response.status_code == 200:
        # raw 데이터를 파일로 작성합니다.
        with open("downloaded_image.jpg", 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
    else:
        print(f"Error downloading image: {response.status_code}")
    
    fbx_file = 'statics/fbx_file/image_001_OCR_join_all.fbx'

    url = 'http://127.0.0.1:8001/blueprint_to_3D'

    data = {
        'ImagePath': fbx_file
        }
    
    return JSONResponse(content=data)


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



# @app.post("/image_to_fbx")
# async def create_upload_file(file: UploadFile = File(...)):
#     # 업로드된 파일의 확장자 확인
#     if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
#         raise HTTPException(status_code=400, detail="Invalid file format!")

#     try:
#         file_dir = f"statics/Images/uploads/"
#         storage_path = Path(file_dir)
#         if not os.path.exists(storage_path):
#             storage_path.mkdir(parents=True, exist_ok=True)

#         file_path = storage_path / file.filename
#         with file_path.open("wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # Preprocessing
#         ouput_path = 'statics/Images/After_preprocessing'
#         preprocessing.run(str(file_path), ouput_path)
#         preprocessing_result = preprocessing.file_save_path('OCR')

#         # Image to blend file
#         url = 'http://127.0.0.1:8001/blueprint_to_3D'

#         data = {'ImagePath': preprocessing_result}

#         response = requests.post(url, json=data)
#         print(f'Status Code: {response.status_code}  /  Response Content : {response.text}')

#         # Blend to fbx converter
#         blend_name = response.text.replace('"','')
#         blend_path = f"statics/blend_file/{blend_name}"
#         print(blend_path)
#         fbx_dir = 'statics/fbx_file'
#         converter.blend_to_fbx(blend_path, fbx_dir)

#     finally:
#         file.file.close()

#     return {"FbxPath": blend_path}


@app.post("/image_to_fbx")
async def create_upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Invalid file format!")

    try:
        storage_path = f"statics/Images/uploads/"
        if not os.path.exists(storage_path):
            storage_path.mkdir(parents=True, exist_ok=True)

        file_path = storage_path +'/'+ file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ItoFBX.image_to_fbx(file_path)

        blend_path = 'statics/fbx_file'

    finally:
        file.file.close()

    return {"FbxPath": blend_path}



# @app.post("/image_to_fbx")
# async def image_to_fbx(item: ImageReceive):
#     now = datetime.now()
#     print('')
#     print(f'in_json_out_json / {now} / {item.userDrawingImage}')
#     print('')

#     response = requests.get(item.userDrawingImage, stream=True)
#     if response.status_code == 200:
#         # raw 데이터를 파일로 작성합니다.
#         with open("downloaded_image.jpg", 'wb') as file:
#             for chunk in response.iter_content(chunk_size=128):
#                 file.write(chunk)
#     else:
#         print(f"Error downloading image: {response.status_code}")
    
#     fbx_file = 'statics/fbx_file/image_001_OCR_join_all.fbx'

#     url = 'http://127.0.0.1:8001/blueprint_to_3D'

#     data = {
#         'ImagePath': fbx_file
#         }
    
#     return JSONResponse(content=data)


from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import Dict
import os
import imghdr  # 이미지 파일 형식을 식별하는 데 사용합니다.
from fastapi.responses import StreamingResponse
import io


@app.post("/files/")
async def create_file(file: UploadFile = File(...)) -> Dict[str, str]:
    try:
        # 파일의 내용을 메모리에 저장합니다.
        contents = await file.read()
        
        # 파일 형식을 식별합니다 (이 경우 이미지 파일에 대해 동작합니다).
        file_type = imghdr.what(None, h=contents)
        if file_type not in ['jpeg', 'png', 'jpg']:
            raise HTTPException(status_code=400, detail="Invalid file format")

        # 파일을 로컬 디렉토리에 저장합니다.
        file_extension = file_type  # 확장자는 실제 파일 형식에 따라 결정됩니다.
        file_name = f"uploaded_file.{file_extension}"
        with open(file_name, "wb") as out_file:
            out_file.write(contents)

        # 이제 FBX 파일을 읽고 스트리밍해야 합니다.
        fbx_file_path = 'statics/fbx_file/image_000_pre_join_all.fbx'
        with open(fbx_file_path, "rb") as fbx:
            fbx_data = fbx.read()  # 파일의 바이트 내용을 읽습니다.

        return StreamingResponse(io.BytesIO(fbx_data), media_type="application/octet-stream")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



class ImageURL(BaseModel):
    userDrawingImage: str

@app.post("/spring/test/img_to_fbx")
async def download_and_return_fbx(image_url: ImageURL):
    url = image_url.userDrawingImage
    print(url)

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    path = urlparse(url).path
    ext = Path(path).suffix.lower()  # ex: '.jpg', '.png'

    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid file type, only .jpg, .jpeg and .png are allowed")

    try:
        response = requests.get(url, stream=True)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not download image")

        local_filename = f'downloaded_image{ext}'
        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Requests exception: {e}")

    try:
        # 이제 FBX 파일을 읽고 스트리밍해야 합니다.
        fbx_file_path = 'statics/fbx_file/image_000_pre_join_all.fbx'
        with open(fbx_file_path, "rb") as fbx:
            fbx_data = fbx.read()  # 파일의 바이트 내용을 읽습니다.

        return StreamingResponse(io.BytesIO(fbx_data), media_type="application/octet-stream")
    #     fbx_file_path = 'statics/fbx_file/image_000_pre_join_all.fbx'

    #     if not os.path.exists(fbx_file_path):
    #         raise HTTPException(status_code=404, detail="FBX file not found")

    #     return FileResponse(fbx_file_path, media_type="application/octet-stream", filename="custom_filename.fbx")
    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")