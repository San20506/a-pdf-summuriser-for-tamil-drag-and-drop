import os
from flask import Flask, render_template, request, jsonify
import fitz  # PyMuPDF
import langid
from summa import summarizer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions for upload
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        full_text += page.get_text()
    return full_text

# Detect language of text
def detect_language(text):
    lang, _ = langid.classify(text)
    return lang

# Summarize text
def summarize_text(text):
    return summarizer.summarize(text)

# Handle the file upload
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Extract text and process
        text = extract_text_from_pdf(filepath)
        
        if detect_language(text) == 'ta':  # 'ta' is the language code for Tamil
            summary = summarize_text(text)
            return jsonify({"summary": summary})
        else:
            return jsonify({"error": "The PDF is not in Tamil."}), 400

    return jsonify({"error": "Invalid file format. Only PDFs are allowed."}), 400

if __name__ == "__main__":
    app.run(debug=True)
