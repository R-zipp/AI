from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional
from PIL import Image
import io

from lib.file_download_and_upload import save_file_in_S3, file_download_with_url
from lib.generate_blueprint import BlueprintGenerator
from image_to_fbx import ImageToFBX
import lib.const as const


app = FastAPI()
ItoFBX = ImageToFBX()
generator = BlueprintGenerator(const.MODEL_PATH)

app.mount("/statics", StaticFiles(directory="statics"), name="statics")



class ImageInfo(BaseModel):
    drawingType: str
    userDrawingImage: str
    houseSize: Optional[str] = None

@app.post("/spring/img_to_fbx_S3")
async def download_and_return_fbx(item: ImageInfo):
    img_type = item.drawingType
    url = item.userDrawingImage
    houseSize = item.houseSize
    print(f'img_type : {img_type}, houseSize : {houseSize}')
    
    # Validation
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    path = urlparse(url).path
    file_name = path.split('/')[-1]
    ext = Path(path).suffix.lower()  # ex: '.jpg', '.png'

    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid file type, only .jpg, .jpeg and .png are allowed")
    
    if img_type not in ["HANDIMG", "FLOORPLAN"]:
        raise HTTPException(status_code=400, detail="Invalid image type, only HANDIMG, FLOORPLAN are allowed")

    # File download
    image = file_download_with_url(url, save=True ,filename=file_name)

    # Main process
    try:
        print('Run main process!')

        fbx_file = ItoFBX.run(img_type, image, name=file_name, size=32*3.3)
        file_url = save_file_in_S3(fbx_file)
            
        return JSONResponse(content={'URL': file_url})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    



@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    img_type = ["HANDIMG", "FLOORPLAN"]
    # Read the contents of the uploaded file
    contents = await file.read()

    # Convert the contents to a BytesIO object
    image_stream = io.BytesIO(contents)

    # Open the image using PIL
    image = Image.open(image_stream)

    try:
        print('Run main process!')

        fbx_file = ItoFBX.run(img_type[0], image, name='test.png', size=32*3.3)
        file_url = save_file_in_S3(fbx_file)
            
        return JSONResponse(content={'URL': file_url})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")