from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os

from blueprint_to3D import BLueprintTo3D

app = FastAPI()
bLueprint_to_3D = BLueprintTo3D()



class Item(BaseModel):
    ImagePath: str

@app.post("/blueprint_to_3D")
async def create_user(item: Item):
    img_path = item.ImagePath
    img_path = '../AR-zipp/'+img_path.replace('\\', '/')

    img_name, extension = os.path.splitext(img_path.split('/')[-1])
    output_path = f'../AR-zipp/statics/blend_file/{img_name}.blend'

    print(img_path)
    project_path, area_size = bLueprint_to_3D.make_blend(img_path)
    shutil.copy(project_path, output_path)

    print('')
    print(f'File copied at : {output_path}')

    return JSONResponse(content={'blend_name': f'{img_name}.blend', 'size': area_size})

