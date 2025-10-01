import os
import io
from flask import Flask, request, Response
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename

# Use /tmp for file uploads (Required for Render for read/write access)
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Flask application object name is 'application'
application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML Template is defined directly in Python using placeholders
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCR Text Extractor</title>
    <style>
        body { font-family: 'Arial', sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .container { background-color: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); width: 100%; max-width: 500px; }
        h1 { text-align: center; color: #333; margin-bottom: 20px; font-size: 24px; }
        .upload-form input[type="file"] { border: 2px solid #ccc; padding: 10px; border-radius: 6px; width: 100%; margin-bottom: 15px; box-sizing: border-box; }
        .upload-form button { background-color: #007bff; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; width: 100%; font-size: 16px; transition: background-color 0.3s; }
        .upload-form button:hover { background-color: #0056b3; }
        .result-box { margin-top: 25px; border: 1px solid #ddd; border-radius: 6px; background-color: #e9ecef; padding: 15px; }
        .result-box h2 { font-size: 18px; color: #555; margin-top: 0; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
        .extracted-text { white-space: pre-wrap; word-wrap: break-word; font-size: 15px; color: #212529; min-height: 50px; }
        .error { color: #dc3545; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 Image to Text (OCR)</h1>
        
        {error_placeholder}

        <form method="POST" enctype="multipart/form-data" class="upload-form">
            <input type="file" name="file" accept=".png, .jpg, .jpeg" required>
            <button type="submit">Extract Text</button>
        </form>

        {result_placeholder}
    </div>
</body>
</html>
"""

def allowed_file(filename):
    """Checks if the uploaded file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def render_page(extracted_text=None, error=None):
    """Renders the HTML page by substituting placeholders."""
    error_html = ""
    result_html = ""
    
    if error:
        error_html = f'<p class="error">{error}</p>'

    if extracted_text:
        result_html = f"""
            <div class="result-box">
                <h2>Extracted Text:</h2>
                <pre class="extracted-text">{extracted_text}</pre>
            </div>
        """
        
    final_html = HTML_TEMPLATE.replace("{error_placeholder}", error_html).replace("{result_placeholder}", result_html)
    
    # Return a Flask Response object with HTML content
    return Response(final_html, mimetype='text/html')

@application.route('/', methods=['GET', 'POST'])
def upload_file():
    extracted_text = None
    error = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No file part in the request.'
        else:
            file = request.files['file']
            if file.filename == '':
                error = 'No file selected for uploading.'
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # CRITICAL FIX: Save the file to the temporary location (/tmp)
                temp_filepath = os.path.join(application.config['UPLOAD_FOLDER'], filename)
                file.save(temp_filepath)
                
                try:
                    # Perform OCR on the saved temporary file
                    img = Image.open(temp_filepath)
                    extracted_text = pytesseract.image_to_string(img)
                except Exception as e:
                    error = f"An error occurred during OCR: {e}"
                finally:
                    # Clean up the temporary file after processing
                    os.remove(temp_filepath)
            else:
                error = 'File type not allowed. Use PNG, JPG, or JPEG.'
                
    return render_page(extracted_text=extracted_text, error=error)


if __name__ == '__main__':
    # Ensure the /tmp directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    application.run(debug=True)