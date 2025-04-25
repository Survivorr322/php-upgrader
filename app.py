Python 3.13.1 (tags/v3.13.1:0671451, Dec  3 2024, 19:06:28) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import os, zipfile, shutil, tempfile
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
        code = re.sub(r'\bereg\((.*?)\)', r'preg_match(\1)', code)
        code = re.sub(r'\bvar\b', 'public', code)
        code = re.sub(r'\bsplit\(', 'explode(', code)
        return code
    except Exception as e:
        print(f"[HATA] Kod dönüştürülürken hata oluştu: {e}")
        return code  # Orijinal kodu bozmadan döndür
... 
... def process_php_files(folder_path):
...     php_files = list(Path(folder_path).rglob("*.php"))
...     for php_file in php_files:
...         with open(php_file, 'r', encoding='utf-8', errors='ignore') as f:
...             code = f.read()
...         with open(php_file, 'w', encoding='utf-8') as f:
...             f.write(transform_php_code(code))
... 
... def extract_and_convert(zip_path):
...     temp_dir = tempfile.mkdtemp()
...     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
...         zip_ref.extractall(temp_dir)
...     process_php_files(temp_dir)
...     output_zip = os.path.join(tempfile.gettempdir(), "converted_project.zip")
...     with zipfile.ZipFile(output_zip, 'w') as zipf:
...         for root, _, files in os.walk(temp_dir):
...             for file in files:
...                 filepath = os.path.join(root, file)
...                 arcname = os.path.relpath(filepath, temp_dir)
...                 zipf.write(filepath, arcname)
...     return output_zip
... 
... HTML = '''
... <!doctype html>
... <title>PHP Dönüştürücü</title>
... <h2>PHP 4.7 → 7/8 Dönüştürücü</h2>
... <form method=post enctype=multipart/form-data>
...   <input type=file name=file required>
...   <input type=submit value='Dönüştür'>
... </form>
... '''
... 
... @app.route('/', methods=['GET', 'POST'])
... def upload_file():
...     if request.method == 'POST':
...         file = request.files['file']
...         if file.filename.endswith('.zip'):
...             path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
...             file.save(path)
...             result_zip = extract_and_convert(path)
...             return send_file(result_zip, as_attachment=True, download_name="php7_project.zip")
...         return "Sadece .zip dosyaları yükleyebilirsiniz."
...     return render_template_string(HTML)
... 
... if __name__ == "__main__":
...     app.run(debug=True)
