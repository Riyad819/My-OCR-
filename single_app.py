import os
import io
from flask import Flask, request, render_template, redirect, url_for
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename
from urllib.parse import quote

# Use /tmp for file uploads (Required for Render for read/write access)
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Flask application object name is 'app' (Changed from 'application' for Gunicorn compatibility)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ----------------------------------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------------------------------

def allowed_file(filename):
    """Checks if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def render_page(extracted_text="", error=""):
    """Renders the main HTML page with results or errors."""
    
    # HTML Template is defined directly in Python for single-file deployment
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OCR Text Extractor</title>
        <style>
            body { 
                font-family: 'Arial', sans-serif; 
                background-color: #f4f7f9; 
                color: #333; 
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: #fff;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #007bff;
                text-align: center;
                margin-bottom: 30px;
            }
            .upload-form {
                display: flex;
                flex-direction: column;
                gap: 15px;
                padding: 20px;
                border: 2px dashed #ddd;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            input[type="file"] {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #f9f9f9;
            }
            button {
                padding: 12px 20px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }
            button:hover {
                background-color: #218838;
            }
            .result-box {
                background-color: #e9ecef;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                word-wrap: break-word;
                white-space: pre-wrap;
                border-left: 5px solid #007bff;
            }
            .error {
                color: white;
                background-color: #dc3545;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 20px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>OCR Text Extractor</h1>
            <form method="post" enctype="multipart/form-data" class="upload-form">
                <input type="file" name="file" required>
                <button type="submit">Extract Text</button>
            </form>

            {error_message}

            {result_content}
        </div>
    </body>
    </html>
    """
    
    error_message = f'<div class="error">{error}</div>' if error else ''
    
    if extracted_text:
        result_content = f"""
        <h2>Extracted Text</h2>
        <pre class="result-box">{extracted_text}</pre>
        """
    else:
        result_content = ""

    return HTML_TEMPLATE.format(error_message=error_message, result_content=result_content)


# ----------------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    return render_page()

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_page(error="No file part in the request.")
    
    file = request.files['file']
    
    if file.filename == '':
        return render_page(error="No file selected.")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file to the temporary location (/tmp)
        try:
            file.save(temp_filepath)
        except Exception as e:
             return render_page(error=f"Error saving file: {e}")
        
        extracted_text = ""
        error = ""

        try:
            # Perform OCR on the saved temporary file
            img = Image.open(temp_filepath)
            # Use language code 'eng' for English OCR
            extracted_text = pytesseract.image_to_string(img, lang='eng')

        except Exception as e:
            error = f"An error occurred during OCR: {e}"
        finally:
            # Clean up the temporary file after processing
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            
        if not extracted_text and not error:
            error = "No text could be extracted from the image."

        return render_page(extracted_text=extracted_text, error=error)
    else:
        error = 'File type not allowed. Use PNG, JPG, or JPEG.'
        return render_page(error=error)