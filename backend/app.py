import os
import spacy
import json
import re
import fitz  # PyMuPDF for PDF reading
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from werkzeug.utils import secure_filename
from scoring import calculate_score, generate_feedback
from job_descriptions import job_roles

# Load NLP models
nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load Job Descriptions
#jd existed here
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

# Function to clean extracted text
def clean_text(text):
    text = re.sub(r'\(cid:[^\)]+\)', '', text)  # Remove (cid:XX) patterns
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
    return text

# Function to extract name using spaCy
def extract_name(text):
    doc = nlp(text)
    person_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    return person_names[0] if person_names else None  # Take the first detected name

# Function to extract email from text
def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None  # Take first valid email

# Function to extract phone number from text
def extract_phone(text):
    phone_pattern = r'\+?\d{1,3}[-.\s]?\(?\d{2,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}'
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else None  # Take first valid phone number

# Function to extract skills from text
def extract_skills(text):
    skill_keywords = ["JavaScript", "React", "Node.js", "MongoDB", "Express.js", "Docker",
                      "Python", "Machine Learning", "SQL", "Flask", "Django"]
    found_skills = [skill for skill in skill_keywords if skill.lower() in text.lower()]
    return found_skills if found_skills else None  # Return list of found skills

# Function to extract education details
def extract_education(text):
    education_keywords = ["B.Tech", "Bachelor", "M.Tech", "Master", "Ph.D", "Diploma"]
    for keyword in education_keywords:
        if keyword.lower() in text.lower():
            return keyword
    return None  # If no match, return None

# Function to extract experience in years
def extract_experience(text):
    exp_pattern = r'(\d+)\+?\s?(years?|yrs?)\s?(of)?\s?(experience)?'
    matches = re.findall(exp_pattern, text, re.IGNORECASE)
    return int(matches[0][0]) if matches else None  # Extract first valid experience

# Function to extract structured resume details
def extract_resume_details(text):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text) or 0,  # Default to 0 if not found
        "education": extract_education(text) or "Not Mentioned"
    }

@app.route("/upload", methods=["POST"])
def upload_resume():
    print("Received request at /upload")
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

    # Clean and process the extracted text
    cleaned_text = clean_text(resume_text)
    structured_data = extract_resume_details(cleaned_text)

    return jsonify({"message": "Resume uploaded successfully", "resume_text": cleaned_text, "structured_data": structured_data})

@app.route("/score", methods=["POST"])
def score_resume():
    """Calculates the resume score based on job role."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    resume_text = data.get("resume_text", "")
    job_role = data.get("job_role", "")

    if not resume_text or not job_role:
        return jsonify({"error": "Missing 'resume_text' or 'job_role'"}), 400
    # Debugging logs
    print(f"Received payload for /score: resume_text length = {len(resume_text)}, job_role = {job_role}")

    # Validate resume_text
    if not resume_text:
        print("Error: Resume text is empty or not extracted correctly.")
        return jsonify({"error": "Resume text is empty or not extracted correctly."}), 400

    # Validate job_role
    if not job_role:
        print("Error: Job role is missing.")
        return jsonify({"error": "Job role is missing."}), 400

    if job_role not in job_roles:
        print(f"Error: Invalid job role '{job_role}'. Available roles: {list(job_roles.keys())}")
        return jsonify({"error": f"Invalid job role '{job_role}'"}), 400

    # Process the resume text to extract structured data
    structured_data = extract_resume_details(resume_text)
    print(f"Structured data extracted: {structured_data}")  # Debugging log

    # Calculate score using structured data
    job_data = job_roles[job_role]
    score = calculate_score(structured_data, job_data)

    return jsonify({"score": score})

@app.route("/feedback", methods=["POST"])
def feedback_resume():
    """Generates textual feedback for resume improvement."""
    print("Received request at /feedback")
    data = request.json
    resume_text = data.get("resume_text", "").strip()

    if not resume_text:
        return jsonify({"error": "No resume text provided or extraction failed."}), 400

    feedback = generate_feedback(resume_text)
    
    return jsonify({"feedback": feedback})

if __name__ == "__main__":
    app.run(debug=True)