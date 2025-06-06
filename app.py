from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import fitz  # PyMuPDF for PDF handling
import google.generativeai as genai

# Flask setup
app = Flask(__name__)
CORS(app)

# Upload folder config
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ Configure Gemini API (make sure to keep API keys private)
genai.configure(api_key="AIzaSyDeXDdbRc0DxMlOjQuIZ746mtbIU6Ox6JI")

# ✅ Create model instance
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# Global text content from PDF or TXT
document_text = ""

# 📄 Upload PDF or TXT
@app.route('/upload', methods=['POST'])
def upload_file():
    global document_text
    file = request.files.get('file')

    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    if file.filename.endswith('.pdf'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        doc = fitz.open(file_path)
        document_text = "\n".join([page.get_text() for page in doc])
    elif file.filename.endswith('.txt'):
        document_text = file.read().decode('utf-8')
    else:
        return jsonify({'error': 'Unsupported file format'}), 400

    return jsonify({'message': 'File uploaded and processed successfully.'})

# ❓ Ask a question
@app.route('/ask', methods=['POST'])
def ask_question():
    global document_text
    data = request.get_json()
    question = data.get('question', '').strip()

    if not document_text:
        return jsonify({'error': 'No document uploaded yet.'}), 400
    if not question:
        return jsonify({'error': 'Question is empty'}), 400

    # Prompt for Gemini
    prompt = f"""Based on the following document, answer the question:\n\n{document_text[:100000]}\n\nQuestion: {question}"""

    try:
        response = model.generate_content(prompt)
        return jsonify({'answer': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🏠 Home page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
