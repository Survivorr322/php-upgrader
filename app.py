import os
import zipfile
import shutil
import tempfile
from flask import Flask, request, send_file, render_template_string
from werkzeug.utils import secure_filename
from pathlib import Path
import re

app = Flask(__name__)
UPLOAD_FOLDER = tempfile.gettempdir()

def transform_php_code(code):
    try:
        code = re.sub(r'\bmysql_([a-zA-Z_]+)', r'mysqli_\1', code)
        code = re.sub(r'<\?(?!php)', '<?php', code)
        code = re.sub(r'&(\$\w+)', r'\1', code)
        # Hatalı: re.sub(r'\bereg\((.*?)\)', r'preg_match(\1)', code)
        # DÜZELTİLDİ:
        code = re.sub(r'\bereg\((.*?)\)', lambda m: f'preg_match({m.group(1)})', code)
        code = re.sub(r'\bvar\b', 'public', code)
        code = re.sub(r'\bsplit\(', 'explode(', code)
        return code
    except Exception as e:
        print(f"[HATA] Kod dönüştürülürken hata oluştu: {e}")
        return code

def process_php_files(folder_path):
    php_files = list(Path(folder_path).rglob("*.php"))
    for php_file in php_files:
        try:
            with open(php_file, 'r', encoding='utf-8', errors='ignore') as f:
                original_code = f.read()

            transformed_code = transform_php_code(original_code)

            with open(php_file, 'w', encoding='utf-8') as f:
                f.write(transformed_code)

            print(f"[✔] Güncellendi: {php_file}")
        except Exception as e:
            print(f"[⛔] {php_file} dosyası işlenirken hata: {e}")

def extract_and_convert(zip_path):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    process_php_files(temp_dir)

    output_zip = os.path.join(tempfile.gettempdir(), "converted_project.zip")
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    return output_zip

# Basit HTML arayüzü
HTML = '''
<!doctype html>
<title>PHP 4.7 → PHP 7/8 Dönüştürücü</title>
<h2>PHP Projesi Dönüştürme Aracı</h2>
<form method=post enctype=multipart/form-data>
  <input type=file name=file required>
  <input type=submit value='Dönüştür ve İndir'>
</form>
<p>Yalnızca .zip formatında PHP projeleri yükleyiniz.</p>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.zip'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(file_path)

            result_zip = extract_and_convert(file_path)
            return send_file(result_zip, as_attachment=True, download_name="php7_project.zip")
        else:
            return "Lütfen sadece .zip dosyaları yükleyin!"
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(debug=True)
