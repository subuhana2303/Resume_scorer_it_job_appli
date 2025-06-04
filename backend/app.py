import os
import re
import logging
from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import spacy
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Constants
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Sample Job Descriptions (You can expand or load from JSON file)
JOB_DESCRIPTIONS = {
    "Data Scientist": """
        Python, Machine Learning, Statistics, Data Analysis, SQL, Deep Learning, TensorFlow, Pandas
    """,
    "Frontend Developer": """
        JavaScript, React, HTML, CSS, Redux, TypeScript, REST APIs, Webpack
    """,
    "Backend Developer": """
        Python, Django, Flask, REST API, SQL, Docker, Microservices, AWS
    """
}

# Helper Functions

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            if not text.strip():
                return None
            return text.strip()
    except Exception as e:
        logging.error(f"Error extracting PDF text: {e}")
        return None

def clean_text(text):
    text = re.sub(r'\(cid:[^\)]+\)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_email(text):
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'\+?\d{1,3}[-.\s]?\(?\d{2,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}', text)
    return match.group(0) if match else None

def extract_skills(text):
    SKILLS_DB = [
        "Python", "JavaScript", "React", "Node.js", "Django", "Flask",
        "Machine Learning", "SQL", "Docker", "AWS", "TensorFlow", "Pandas"
    ]
    found = [skill for skill in SKILLS_DB if skill.lower() in text.lower()]
    return found or []

def extract_experience(text):
    match = re.search(r'(\d+)\+?\s?(years?|yrs?)', text, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def extract_education(text):
    EDUCATION_TERMS = ["Bachelor", "B.Tech", "Master", "M.Tech", "PhD", "Diploma"]
    for term in EDUCATION_TERMS:
        if term.lower() in text.lower():
            return term
    return "Not Mentioned"

def extract_resume_details(text):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text)
    }

def calculate_similarity(resume_text, job_desc_text):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform([resume_text, job_desc_text])
    cosine_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(cosine_sim * 100, 2)  # return percentage

def generate_checklist(score):
    checklist = []
    if score < 40:
        checklist.append("Add more relevant skills.")
        checklist.append("Include more experience details.")
    elif score < 70:
        checklist.append("Highlight key projects and achievements.")
    else:
        checklist.append("Resume looks strong. Consider tailoring it for specific jobs.")
    return checklist

def generate_feedback(score, structured_data):
    feedback = f"Your resume match score is {score}%. "
    if score < 40:
        feedback += "Your resume needs significant improvement in skills and experience sections."
    elif score < 70:
        feedback += "Good resume, but adding more relevant details could improve your chances."
    else:
        feedback += "Excellent match! Your resume aligns well with the job requirements."
    return feedback

# Flask App Setup

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/upload", methods=["POST"])
def upload_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Upload PDF only."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    logging.info(f"Saved file: {filepath}")

    text = extract_text_from_pdf(filepath)
    if not text:
        return jsonify({"error": "Failed to extract text from PDF. Make sure it is not a scanned image."}), 400

    cleaned_text = clean_text(text)
    details = extract_resume_details(cleaned_text)

    return jsonify({
        "message": "File uploaded and processed",
        "resume_text": cleaned_text,
        "details": details
    })

@app.route("/score", methods=["POST"])
def score_resume():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400
    resume_text = data.get("resume_text", "")
    job_role = data.get("job_role", "")
    if not resume_text or not job_role:
        return jsonify({"error": "Both 'resume_text' and 'job_role' are required"}), 400
    if job_role not in JOB_DESCRIPTIONS:
        return jsonify({"error": f"Invalid job role. Available roles: {list(JOB_DESCRIPTIONS.keys())}"}), 400

    job_desc_text = JOB_DESCRIPTIONS[job_role]
    score = calculate_similarity(resume_text, job_desc_text)
    checklist = generate_checklist(score)
    feedback = generate_feedback(score, None)

    return jsonify({
        "score": score,
        "checklist": checklist,
        "feedback": feedback
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
