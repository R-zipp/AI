from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException
import json
import boto3
import requests


with open('resources/secret.json', 'r') as file:
    data = json.load(file)

ACCESS_KEY = data['AWS_ACCESSKEY']
SECRET_KEY = data['AWS_SECRETKEY']
BUCKET_NAME = 'arzip-bucket'
REGION_NAME = 'ap-northeast-2'



def save_file_in_S3(fbx_file_path):
    try:
        with open(fbx_file_path, "rb") as fbx:
            fbx_data = fbx.read()

        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

        file_name = fbx_file_path.split('/')[-1]
        object_name = f'AI/{file_name}'

        try:
            s3.put_object(Bucket=BUCKET_NAME, Key=object_name, Body=fbx_data)
            file_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{object_name}"
            print('Save fbx file in AWS S3 done')
        except NoCredentialsError:
            raise HTTPException(status_code=401, detail="Credential problem")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Something went wrong!!")

        return file_url

    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    

def file_download_with_url(url, local_filename):
    try:
        response = requests.get(url, stream=True)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not download image")

        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Requests exception: {e}")



if __name__ == '__main__':
    fbx_file_path = 'statics/fbx_file/image_000_pre_join_all.fbx'
    save_file_in_S3(fbx_file_path)