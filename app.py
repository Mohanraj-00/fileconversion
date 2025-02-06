from flask import Flask, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from fpdf import FPDF
import docx
from PyPDF2 import PdfReader

app = Flask(__name__)

# Set up your upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}  # Add other extensions as needed

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit to 16 MB

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create a simple PDF to Word converter (as an example)
def convert_pdf_to_word(pdf_file_path):
    # Extract text from PDF using PyPDF2
    reader = PdfReader(pdf_file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Create a Word document with the extracted text using python-docx
    doc = docx.Document()
    doc.add_paragraph(text)
    word_file_path = os.path.splitext(pdf_file_path)[0] + '.docx'
    doc.save(word_file_path)
    
    return word_file_path

@app.route('/')
def home():
    return "Welcome to the File Converter API!"  # Home route

@app.route('/convert', methods=['POST'])
def convert():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('files')
    conversion_type = request.form.get('conversion_type', None)

    if not conversion_type:
        return jsonify({"error": "Conversion type not specified"}), 400
    
    # Process each file
    converted_files = []
    for file in files:
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Conversion logic
            if conversion_type == 'pdf_to_word':
                converted_file = convert_pdf_to_word(file_path)
                converted_files.append(converted_file)
            else:
                return jsonify({"error": "Unsupported conversion type"}), 400
        else:
            return jsonify({"error": "File not allowed"}), 400
    
    # Send back the converted file(s)
    if len(converted_files) == 1:
        return send_file(converted_files[0], as_attachment=True)
    else:
        return jsonify({"message": "Files converted successfully", "converted_files": converted_files})

if __name__ == '__main__':
    app.run(debug=True)
