from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional
from PIL import Image
import io
import uvicorn

from Lib.file_download_and_upload import save_file_in_S3, file_download_with_url
from Lib.generate_blueprint import BlueprintGenerator
from image_to_fbx import ImageToFBX
import Lib.const as const
import Lib.dialog as dialog


app = FastAPI()
ItoFBX = ImageToFBX()
generator = BlueprintGenerator(const.MODEL_PATH)

app.mount("/Statics", StaticFiles(directory="Statics"), name="Statics")

dialog.figlet()
dialog.init()


class ImageInfo(BaseModel):
    drawingType: str
    userDrawingImage: str
    houseSize: Optional[str] = None
    wallPaperNo: Optional[int] = None


@app.post("/spring/img_to_fbx_S3")
async def download_and_return_fbx(item: ImageInfo):
    img_type = item.drawingType
    url = item.userDrawingImage
    house_size = item.houseSize.split('_')[0]
    house_size_type = item.houseSize.split('_')[1]
    wallpaper_no = item.wallPaperNo
    
    print(f'img_type : {img_type}, houseSize : {house_size}, house_type : {house_size_type}, wallPaperNo : {wallpaper_no}')
    
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
    
    if house_size_type == 'squaremeter':
        house_size = int(house_size)
    elif house_size_type == 'pyeong':
        house_size = int(house_size) * 3.3
    else:
        raise HTTPException(status_code=400, detail="Invalid size type, only squaremeter, pyeong are allowed")

    # File download
    image = file_download_with_url(url, save=True ,filename=file_name)

    # Main process
    # try:
    print('Run main process!')

    fbx_file = ItoFBX.run(
                            img_type, 
                            image, 
                            name=file_name, 
                            size=house_size, 
                            wallpaper_no=wallpaper_no
                            )
    file_url = save_file_in_S3(fbx_file)
    
    return JSONResponse(content={'URL': file_url})

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Server error: {e}")
    



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

        fbx_file = ItoFBX.run(img_type[1], image, name='test.png', size=5*3.3)
        file_url = save_file_in_S3(fbx_file)
            
        return JSONResponse(content={'URL': file_url})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn.run(app, port=8000)