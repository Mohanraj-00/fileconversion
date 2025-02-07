from flask import Flask, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
import PyPDF2
import docx
import pandas as pd
import pytesseract
from PIL import Image
import pdf2image
from pdf2docx import Converter
from fpdf import FPDF
import shutil
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to convert PDF to Word
def pdf_to_word(pdf_path, output_path):
    cv = Converter(pdf_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()
    return output_path

# Function to convert PDF to Text using OCR
def pdf_to_text_ocr(pdf_path, output_path):
    images = pdf2image.convert_from_path(pdf_path)
    text = "\n".join([pytesseract.image_to_string(img) for img in images])
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    return output_path

# Function to convert Image to Text
def image_to_text(image_path, output_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    return output_path

# Function to convert Excel to CSV
def excel_to_csv(excel_path, output_path):
    df = pd.read_excel(excel_path)
    df.to_csv(output_path, index=False)
    return output_path

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the File Converter API!"})

@app.route("/convert", methods=["POST"])
def convert_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_ext = filename.split(".")[-1].lower()
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    output_filename = str(uuid.uuid4())
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    try:
        if file_ext == "pdf":
            output_path += ".docx"
            pdf_to_word(file_path, output_path)
        elif file_ext in ["png", "jpg", "jpeg"]:
            output_path += ".txt"
            image_to_text(file_path, output_path)
        elif file_ext in ["xls", "xlsx"]:
            output_path += ".csv"
            excel_to_csv(file_path, output_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400
        
        return send_file(output_path, as_attachment=True, mimetype='application/octet-stream')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    import sys
    import subprocess
    try:
        import pandas
    except ModuleNotFoundError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
        import pandas
    
    app.run(host="0.0.0.0", port=5000)
