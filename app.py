import os
import io
from flask import Flask, request, render_template
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename

# Change the UPLOAD_FOLDER to /tmp for Render (Read-Write access)
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@application.route('/', methods=['GET', 'POST'])
def upload_file():
    extracted_text = None
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', error='No file part in the request.')
        
        file = request.files['file']
        
        # Check if user selects a file
        if file.filename == '':
            return render_template('index.html', error='No file selected for uploading.')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Save the file to the temporary location (/tmp)
            temp_filepath = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)
            
            # Perform OCR on the saved file
            try:
                img = Image.open(temp_filepath)
                # Use pytesseract to extract text
                extracted_text = pytesseract.image_to_string(img)
            except Exception as e:
                extracted_text = f"An error occurred during OCR: {e}"
            finally:
                # Clean up the temporary file after processing
                os.remove(temp_filepath)

    return render_template('index.html', extracted_text=extracted_text)

if __name__ == '__main__':
    # Ensure the /tmp directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    application.run(debug=True)