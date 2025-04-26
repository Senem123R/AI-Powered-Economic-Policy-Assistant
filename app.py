from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import fitz  # PyMuPDF for PDF handling
import google.generativeai as genai
import spacy

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Configure Gemini AI
API_KEY = "AIzaSyBE8MCfKecU2vnD3XZmJ0-f8C_8WMCSdBE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML file


def extract_text_from_pdf(file):
    """Extracts text from a PDF file."""
    pdf_text = ""
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            pdf_text += page.get_text()
        doc.close()
    except Exception as e:
        return f"Error reading PDF: {e}"
    return pdf_text

def clean_text(text):
    """Cleans extracted text by removing stopwords and lemmatizing."""
    doc = nlp(text.lower())
    words = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(words)

@app.route('/summarize', methods=['POST'])
def summarize():
    """Handles PDF file uploads and returns a summary."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    raw_text = extract_text_from_pdf(file)
    cleaned_text = clean_text(raw_text)

    # Summarization using Gemini
    prompt = f"Summarize this document:\n{cleaned_text[:30000]}"
    response = model.generate_content(prompt)
    
    return jsonify({"summary": response.text})

@app.route('/generate-policy', methods=['POST'])
def generate_policy():
    """Generates an economic policy based on user input."""
    policy_type = request.form.get("policy_type")
    scenario = request.form.get("scenario")

    if not policy_type or not scenario:
        return jsonify({"error": "Policy type and scenario required"}), 400

    prompt = f"Generate an economic policy from {policy_type} for the scenario: {scenario}"
    response = model.generate_content(prompt)
    
    return jsonify({"generated_policy": response.text})

if __name__ == '__main__':
    app.run(debug=True)