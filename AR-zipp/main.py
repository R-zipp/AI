from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict
import imghdr
import io
import requests
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime
import shutil
import os

from lib.etc import save_file_in_S3
from lib.image_to_fbx import ImageToFBX



app = FastAPI()
ItoFBX = ImageToFBX()

app.mount("/statics", StaticFiles(directory="statics"), name="statics")


# Unreal Part

# @app.post("/unreal/test/img_to_fbx")
# async def create_file(file: UploadFile = File(...)) -> Dict[str, str]:
#     print('hahahaha')
#     try:
#         contents = await file.read()
        
#         file_type = imghdr.what(None, h=contents)
#         if file_type not in ['jpeg', 'png', 'jpg']:
#             raise HTTPException(status_code=400, detail="Invalid file format")

#         file_name = f"uploaded_file.{file_type}"
#         with open(file_name, "wb") as out_file:
#             out_file.write(contents)

#         fbx_file_path = 'statics/fbx_file/image_000_pre_join_all.fbx'
#         with open(fbx_file_path, "rb") as fbx:
#             fbx_data = fbx.read()

#         return StreamingResponse(io.BytesIO(fbx_data), media_type="application/octet-stream")
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/unreal/test/img_to_fbx")
async def upload_image(request: Request):
    content_type = request.headers.get('content-type')
    now = datetime.now()
    print(f'{now} / content_type : {content_type}')
    if content_type not in  ['image/jpeg', 'image/png', 'image/jpg']:
        raise HTTPException(status_code=400, detail="Content-Type is not image/jpeg")
    print('success')
    return 'success'
    # body = await request.body()

    # try:
    #     # 이미지 파일 저장할 경로 지정 (예: 현재 작업 디렉토리 아래의 'uploads' 폴더)
    #     upload_folder = Path(os.getcwd()) / "uploads"
    #     upload_folder.mkdir(parents=True, exist_ok=True)

    #     # # 파일 경로 생성
    #     file_path = upload_folder / "uploaded_image.jpg"

    #     with open(file_path, "wb") as image_file:
    #         image_file.write(body)
        

    #     data = {
    #         'Status': 'success'
    #         }
    #     print(data)
    #     return JSONResponse(content=data)
    
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/unreal/img_to_fbx")
async def create_file(file: UploadFile = File(...)) -> Dict[str, str]:
    try:
        contents = await file.read()

        file_type = imghdr.what(None, h=contents)
        if file_type not in ['jpeg', 'png', 'jpg']:
            raise HTTPException(status_code=400, detail="Invalid file format")

        file_name = f"uploaded_file.{file_type}"
        with open(file_name, "wb") as out_file:
            out_file.write(contents)

        # 이제 FBX 파일을 읽고 스트리밍해야 합니다.
        fbx_file_path = 'statics/fbx_file/image_000_pre_join_all.fbx'
        with open(fbx_file_path, "rb") as fbx:
            fbx_data = fbx.read()  # 파일의 바이트 내용을 읽습니다.

        return StreamingResponse(io.BytesIO(fbx_data), media_type="application/octet-stream")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Spring Part

class ImageURL(BaseModel):
    userDrawingImage: str

@app.post("/spring/img_to_fbx_S3")
async def download_and_return_fbx(image_url: ImageURL):
    # Validation
    url = image_url.userDrawingImage

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    path = urlparse(url).path
    file_name = path.split('/')[-1]
    ext = Path(path).suffix.lower()  # ex: '.jpg', '.png'

    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid file type, only .jpg, .jpeg and .png are allowed")

    # File download
    try:
        response = requests.get(url, stream=True)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not download image")

        local_filename = f'statics/uploads/{file_name}'
        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Requests exception: {e}")

    # Main process
    try:
        print('Run main process!')
        fbx_file = ItoFBX.image_to_fbx(local_filename).replace('\\', '/')

        file_url = save_file_in_S3(fbx_file)

        return JSONResponse(content={'URL': file_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    

@app.post("/spring/img_to_fbx_S3_test")
async def download_and_return_fbx(image_url: ImageURL):
    # Validation
    url = image_url.userDrawingImage

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    path = urlparse(url).path
    file_name = path.split('/')[-1]
    ext = Path(path).suffix.lower()  # ex: '.jpg', '.png'

    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid file type, only .jpg, .jpeg and .png are allowed")

    # File download
    try:
        response = requests.get(url, stream=True)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not download image")

        local_filename = f'statics/uploads/{file_name}'
        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Requests exception: {e}")

    # Main process
    try:
        print('Run main process!')
        # fbx_file = ItoFBX.image_to_fbx(local_filename).replace('\\', '/')
        fbx_file_path = 'statics/fbx_file/image_000_pre_join_all.fbx'
        # with open(fbx_file_path, "rb") as fbx:
            # fbx_data = fbx.read()

        file_url = save_file_in_S3(fbx_file_path)
        print(file_url)
        return JSONResponse(content={'URL': file_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    





@app.post("/spring/img_to_fbx_S3_origin_own_test")
async def download_and_return_fbx(file: UploadFile = File(...)):
    # Validation
    file_name = file.filename
    ext = Path(file_name).suffix.lower()  # ex: '.jpg', '.png'

    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid file type, only .jpg, .jpeg and .png are allowed")

    # File save
    local_filename = f'statics/uploads/{file_name}'
    try:
        with open(local_filename, 'wb') as buffer:
            buffer.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    # Main process
    try:
        print('Run main process!')
        fbx_file = ItoFBX.image_to_fbx(local_filename).replace('\\', '/')

        file_url = save_file_in_S3(fbx_file)

        return JSONResponse(content={'URL': file_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    
    
    
    

@app.post("/spring/img_to_fbx_S3_test_2")
async def download_and_return_fbx(image_url: ImageURL):
    # Validation
    url = image_url.userDrawingImage

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    path = urlparse(url).path
    file_name = path.split('/')[-1]
    ext = Path(path).suffix.lower()  # ex: '.jpg', '.png'

    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid file type, only .jpg, .jpeg and .png are allowed")

    # File download
    try:
        response = requests.get(url, stream=True)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not download image")

        local_filename = f'statics/uploads/{file_name}'
        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Requests exception: {e}")

    # Main process
    try:
        print('Run main process!')
        # fbx_file = ItoFBX.image_to_fbx(local_filename).replace('\\', '/')
        fbx_file_path = 'statics/fbx_file/image_000_pre_join_all.fbx'
        # with open(fbx_file_path, "rb") as fbx:
            # fbx_data = fbx.read()

        file_url = save_file_in_S3(fbx_file_path)
        print(file_url)
        
        # Send unreal-python sever
        url = 'http://192.168.0.48:8000/fbx_download'

        data = {'FBXfileURL': file_url}

        response = requests.post(url, json=data)
        print(f'Status Code: {response.status_code}  /  Response Content : {response.text}')
        if response.status_code == 200:
            pass
        
        return JSONResponse(content={'URL': file_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    