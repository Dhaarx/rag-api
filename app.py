import base64
import io
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader # type: ignore
import fitz  # type: ignore # PyMuPDF
from PIL import Image

app = Flask(__name__)
CORS(app)

# Function to extract text from PDF
def extract_pdf_content(pdf_path):
    reader = PdfReader(pdf_path)
    extracted_text = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text.append(text)

    return extracted_text

pdf_path = "sih3.pdf"  
extracted_text = extract_pdf_content(pdf_path)

# Function to fetch image from PDF based on the query
def extract_images_from_pdf_based_on_query(pdf1_path, query=None):
    pdf_document = fitz.open(pdf1_path)
    matching_images = []

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        text = page.get_text("text")

        if query is None or query.lower() in text.lower():
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))

                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                matching_images.append(img_base64)

    pdf_document.close()
    return matching_images


@app.route('/')
def home():
    return "welcome to the crop prediction API"


@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content for favicon

@app.route('/rag', methods=['POST'])
def rag():
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({"error": "Empty query"}), 400

    # Search in extracted text based on query
    matches = [page for page in extracted_text if query.lower() in page.lower()]
    images = extract_images_from_pdf_based_on_query(pdf_path, query)

    if matches:
        return jsonify({"status": "ok", "result": matches[0], "images": images})
    else:
        return jsonify({"status": "error", "message": "Content not found"}), 404

if __name__ == '__main__':
    port=int(os.environ.get("PORT",10000))
    app.run(host='0.0.0.0',port=port)
