from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from urllib.parse import urlparse
from pathlib import Path

from lib.file_download_and_upload import save_file_in_S3, file_download_with_url
from lib.image_to_fbx import ImageToFBX



app = FastAPI()
ItoFBX = ImageToFBX()

app.mount("/statics", StaticFiles(directory="statics"), name="statics")


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
    local_filename = f'statics/uploads/{file_name}'
    file_download_with_url(url, local_filename)

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
    local_filename = f'statics/uploads/{file_name}'
    file_download_with_url(url, local_filename)

    # Main process
    try:
        print('Run main process!')
        # fbx_file = ItoFBX.image_to_fbx(local_filename).replace('\\', '/')

        fbx_file_path = 'statics/fbx_file/image_000_pre_join_all.fbx'
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
    