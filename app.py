from flask import Flask, request, render_template, send_file, jsonify, url_for
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image
import os
import uuid
import zipfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB 제한

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # 고유 ID로 폴더 생성
    unique_id = str(uuid.uuid4())
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], unique_id)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # PDF → JPG 변환
        images = convert_from_path(file_path, dpi=200)
        image_paths = []

        for idx, img in enumerate(images):
            img_filename = f'page{idx + 1}.jpg'
            img_path = os.path.join(output_dir, img_filename)
            img.save(img_path, 'JPEG')
            image_paths.append(url_for('static', filename=f'outputs/{unique_id}/{img_filename}'))

        # 이미지들을 zip으로 압축
        zip_path = os.path.join(output_dir, 'converted.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for idx, img_url in enumerate(image_paths):
                real_path = os.path.join('static', 'outputs', unique_id, f'page{idx + 1}.jpg')
                zipf.write(real_path, os.path.basename(real_path))

        return jsonify({
            'images': image_paths,
            'download_url': url_for('static', filename=f'outputs/{unique_id}/converted.zip')
        })
    except Exception as e:
        print('변환 실패:', e)
        return jsonify({'error': 'PDF 변환 실패'}), 500


if __name__ == '__main__':
    app.run(debug=True)
