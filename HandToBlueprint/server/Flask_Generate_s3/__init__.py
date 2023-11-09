from flask import Flask, request, jsonify, send_file, render_template

import os
import io
import boto3

from .views import img_generate_1 as IG_1
# from Flask_Generate import img_generate_2 as IG_2

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# def upload_to_s3(file, s3_key):
#     s3.upload_fileobj(file, BUCKET_NAME, s3_key)

# def download_from_s3(s3_key, local_path):
#     s3.download_file(BUCKET_NAME, s3_key, local_path)

# # json 형태
# @app.route('/generate', methods=['POST'])
# def generate():
#     # request에서 json 데이터를 가져옵니다.
#     data = request.get_json()
#     input_path = data['input_path']
#     output_path = data['output_path']
#     model_path = data['model_path']

#     # generate_image 함수를 호출하여 이미지를 생성합니다.
#     try:
#         IG_1.generate_image(input_path, output_path, model_path)
#         return jsonify({'message': 'Image generated successfully', 'output_path': output_path}), 200
#     except Exception as e:
#         return jsonify({'message': f'Error: {str(e)}'}), 400

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')



# ## img save
# @app.route('/upload', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return 'No image part', 400
    
#     image = request.files['image']
    
#     if image.filename == '':
#         return 'No selected image', 400
    
#     if image:
#         model_path = "./Flask_Generate_s3/G_no_ocr_best_size1024_1105.pt"
#         image_path = os.path.join(UPLOAD_FOLDER, image.filename)
#         image.save(image_path)
#         output_path = os.path.join(UPLOAD_FOLDER, image.filename[:-4] + "_Answer222.jpg")
#         IG_1.generate_image(image_path, output_path, model_path)

#         return 'Image uploaded and saved.'

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)



## img to img
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No image part', 400
    
    image = request.files['image']
    
    if image.filename == '':
        return 'No selected image', 400
    
    if image:
        model_path = "./Flask_Generate_s3/G_no_ocr_best_size1024_1105.pt"
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)
        output_filename = image.filename[:-4] + "_Answer33.jpg"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        IG_1.generate_image(image_path, output_path, model_path)

        # 결과 이미지를 바이트로 변환합니다.
        try:
            with open(output_path, 'rb') as f:
                img_byte_arr = io.BytesIO(f.read())
        except FileNotFoundError:
            return jsonify({"error": "The processed image file was not found."}), 404
        
        img_byte_arr.seek(0)

        # 변환된 이미지를 클라이언트에게 전송합니다.
        return send_file(
            img_byte_arr,
            as_attachment=True,
            download_name=output_filename,
            mimetype='image/jpeg'
        )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)




# @app.route('/upload', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return 'No image part', 400
    
#     image = request.files['image']
    
#     if image.filename == '':
#         return 'No selected image', 400
    
#     if image:
#         # AWS S3에 이미지 업로드
#         # s3_input_key = "uploads/" + image.filename
#         # upload_to_s3(image, s3_input_key)
        
#         # S3이미지 위치
#         s3_input_key = ""

#         # S3에서 이미지 다운로드하여 로컬에 저장
#         local_input_path = os.path.join("/tmp", image.filename)
#         download_from_s3(s3_input_key, local_input_path)
        
#         # AI 추론
#         model_path = "./Flask_Generate/G_no_ocr_best_size1024_1105.pt"
#         local_output_path = os.path.join("/tmp", image.filename[:-4] + "_Answer.jpg")
#         IG_1.generate_image(local_input_path, local_output_path, model_path)
        
#         # 결과 이미지를 S3에 업로드
#         s3_output_key = "results/" + image.filename[:-4] + "_Answer.jpg"
#         with open(local_output_path, "rb") as f:
#             upload_to_s3(f, s3_output_key)

#         return jsonify({'message': 'Image uploaded and processed.', 'output_path': s3_output_key})

# @app.route('/download/<path:filename>', methods=['GET'])
# def download_image(filename):
#     local_path = os.path.join("/tmp", filename)
#     download_from_s3(filename, local_path)
#     return send_file(local_path, as_attachment=True)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)




# AWS S3 설정
AWS_ACCESS_KEY = "AKIAWZA3EFRCGUCD4UOB"
AWS_SECRET_KEY = "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"
S3_BUCKET_NAME = 'arzip-bucket'
S3_REGION_NAME = 'ap-northeast-2'

s3_client = boto3.client('s3',
                         aws_access_key_id=AWS_ACCESS_KEY,
                         aws_secret_access_key=AWS_SECRET_KEY,
                         region_name=S3_REGION_NAME)


@app.route('/infer', methods=['POST'])
def infer():
    # S3에서 이미지 다운로드
    data = request.get_json()
    s3_image_form = data['image_form']
    s3_image_feet = data ['image_feet']
    s3_image_path = data['URL']
    
    if s3_image_form == 'HandIMG':
        local_image_path1 = os.path.basename(s3_image_path)
        local_image_path2 = os.path.join("/uploads", local_image_path1)
        # local_image_path1 = "HandIMGTest.jpg"
        # local_image_path2 = "/test11.jpg"
        s3_client.download_file(S3_BUCKET_NAME,  local_image_path2, local_image_path2)


        model_path = "./Flask_Generate_s3/G_no_ocr_best_size1024_1105.pt"
        output_path = local_image_path2[:-4] + '_Answer.jpg'
        IG_1.generate_image(local_image_path2, output_path, model_path)

        # 결과 이미지를 S3에 업로드 
        s3_output_path = "output/" + os.path.basename(output_path)
        s3_client.upload_file(local_image_path2, S3_BUCKET_NAME, s3_output_path)

        # 결과 이미지의 URL 생성
        s3_output_url = f"https:/{S3_BUCKET_NAME}.s3.{S3_REGION_NAME}.amazonaws.com/test/{s3_output_path}"
        # file_url =      f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{object_name}"

        # JSON 형식으로 결과 반환
        return jsonify({
            's3_output_path': s3_output_url
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
