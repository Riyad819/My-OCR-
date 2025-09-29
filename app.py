# app.py

from flask import Flask, request, jsonify
import os
from PIL import Image # Pillow library
import pytesseract
import numpy as np 

# Configuration
# Folder to temporarily save the uploaded image for processing
UPLOAD_FOLDER = 'uploads' 
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- ছবি থেকে লেখা সনাক্ত করার মূল ফাংশন ---
def get_ocr_text_simple(image_path):
    try:
        # 1. PIL (Pillow) ব্যবহার করে ছবি লোড করা
        img = Image.open(image_path)
        
        # 2. সরাসরি Pytesseract ব্যবহার করে লেখা সনাক্ত করা
        text = pytesseract.image_to_string(img, lang='eng+ben') 
        
        if not text.strip():
            return "No readable text detected. Try using a clear image for better results.", True
        
        return text, True

    except Exception as e:
        # Tesseract Engine বা অন্য কোনো সাধারণ ত্রুটি হলে
        return f"OCR Processing Error: {str(e)}", False


# Route to handle the image file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # ফাইলটি সার্ভারে অস্থায়ীভাবে সেভ করা
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # 4. OCR ফাংশন কল করা
        recognized_text, success = get_ocr_text_simple(filepath)
        
        # 5. Clean up: Temporary ফাইল মুছে ফেলা
        os.remove(filepath) 

        if success:
            return jsonify({
                "message": "Processing complete",
                "text": recognized_text 
            })
        else:
            return jsonify({
                "message": "Processing failed",
                "error": recognized_text 
            }), 500

if __name__ == '__main__':
    # সার্ভার শুরু করা
    app.run(host='0.0.0.0', port=5000)
