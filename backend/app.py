import os
import spacy
import json
import fitz  # PyMuPDF for PDF reading
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from werkzeug.utils import secure_filename
from scoring import calculate_score, generate_feedback

# Load NLP models
nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load Job Descriptions
if os.path.exists("job_descriptions.json"):
    try:
        with open("job_descriptions.json", "r", encoding="utf-8") as file:
            job_roles = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error loading job descriptions: {e}")
        job_roles = {}
else:
    print("Warning: job_descriptions.json not found.")
    job_roles = {}

# Flask App Initialization
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = ""
    print(f"Attempting to open PDF file at: {pdf_path}")
    try:
        with fitz.open(pdf_path) as doc:
            print(f"PDF file opened successfully. Number of pages: {len(doc)}")
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text("text")
                print(f"Page {page_num} extracted text: {page_text[:100]}")  # Log first 100 characters
                text += page_text + "\n"
        if not text.strip():
            print("No text extracted from the PDF. It might be an image-based PDF.")
            return None  # Return None if no text is extracted
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None
    print(f"Final extracted text: {text[:500]}")  # Log first 500 characters of the final text
    return text.strip()


@app.route("/upload", methods=["POST"])
def upload_resume():
    """Handles resume file upload."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    print(f"Saving uploaded file to: {file_path}")
    file.save(file_path)

    resume_text = extract_text_from_pdf(file_path)
    
    if not resume_text:
        return jsonify({"error": "No extracted resume data found. Please check the PDF content."}), 400

    return jsonify({"message": "Resume uploaded successfully", "resume_text": resume_text})


@app.route("/score", methods=["POST"])
def score_resume():
    """Calculates the resume score based on job role."""
    data = request.json
    resume_text = data.get("resume_text", "").strip()
    job_role = data.get("job_role", "").strip()

    if not resume_text:
        return jsonify({"error": "Resume text is empty or not extracted correctly."}), 400

    if job_role not in job_roles:
        return jsonify({"error": f"Invalid job role '{job_role}'"}), 400

    job_data = job_roles[job_role]
    score = calculate_score({"text": resume_text}, job_data)

    return jsonify({"score": score})

@app.route("/feedback", methods=["POST"])
def feedback_resume():
    """Generates textual feedback for resume improvement."""
    data = request.json
    resume_text = data.get("resume_text", "").strip()

    if not resume_text:
        return jsonify({"error": "No resume text provided or extraction failed."}), 400

    feedback = generate_feedback(resume_text)
    
    return jsonify({"feedback": feedback})

if __name__ == "__main__":
    app.run(debug=True)
