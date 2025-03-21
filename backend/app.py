from flask import Flask, request, jsonify
import re
import spacy
import fitz  # PyMuPDF for PDF text extraction
from scoring import calculate_score

app = Flask(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_file.seek(0)  # Reset file pointer before reading
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

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
        "skills": extract_skills(text),
        "experience": extract_experience(text) or 0,  # Default to 0 if not found
        "education": extract_education(text) or "Not Mentioned"
    }

# API to score resume
@app.route('/score', methods=['POST'])
def score_resume():
    data = request.json
    resume_data = data.get("resume")

    if not resume_data:
        return jsonify({"error": "Missing resume data"}), 400

    job_data = {
        "skills": ["Python", "Machine Learning", "SQL"],  # Example JD
        "min_experience": 2,
        "education": "Bachelor's"
    }

    score = calculate_score(resume_data, job_data)
    return jsonify({"score": score})

# API to handle file upload and return structured data
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file:
        text = extract_text_from_pdf(file)
        cleaned_text = clean_text(text)

        extracted_resume = extract_resume_details(cleaned_text)  # Get structured details

        extracted_data = {
            "name": extract_name(cleaned_text),
            "email": extract_email(cleaned_text),
            "phone": extract_phone(cleaned_text),
            "resume": extracted_resume,
            "raw_text": cleaned_text
        }

        return jsonify({"message": "File processed successfully", "data": extracted_data})

if __name__ == '__main__':
    app.run(debug=True)
