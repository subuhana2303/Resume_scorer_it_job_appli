import streamlit as st
import requests
from io import BytesIO
from matplotlib import pyplot as plt

# Page config and styling
st.set_page_config(page_title="Resume Scorer for IT Jobs", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
    body, .css-1d391kg {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        min-height: 100vh;
        padding: 2rem 5rem;
    }
    .stButton>button {
        background: #764ba2;
        color: white;
        font-weight: 700;
        border-radius: 10px;
        padding: 10px 20px;
        transition: background 0.3s ease;
    }
    .stButton>button:hover {
        background: #667eea;
    }
    .header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subheader {
        font-size: 1.3rem;
        text-align: center;
        margin-bottom: 3rem;
        color: #d1c4e9;
    }
    .score-box {
        background: rgba(255, 255, 255, 0.15);
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2rem;
    }
    .bar-container {
        background: #d1c4e9;
        border-radius: 10px;
        height: 25px;
        width: 100%;
        margin-top: 10px;
    }
    .bar-fill {
        height: 100%;
        background: #764ba2;
        border-radius: 10px;
        text-align: center;
        font-weight: 700;
        color: white;
        line-height: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and intro
st.markdown('<div class="header">📄 Resume Scorer for IT Job Applicants</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Upload your PDF resume, select your job role, and get scored instantly!</div>', unsafe_allow_html=True)

# Job roles
JOB_ROLES = ["Frontend Developer", "Backend Developer", "Full Stack Developer", "UI/UX Designer", "Other"]

# Upload and select UI
with st.form("upload_form"):
    uploaded_file = st.file_uploader("📄 Upload your Resume (PDF only)", type=["pdf"])
    job_role = st.selectbox("💼 Select Job Role", JOB_ROLES)
    custom_role = ""
    if job_role == "Other":
        custom_role = st.text_input("Enter your job role")
    submitted = st.form_submit_button("🚀 Get Resume Score")

if submitted:
    if not uploaded_file:
        st.error("Please upload a PDF resume.")
    else:
        actual_role = custom_role if job_role == "Other" and custom_role.strip() else job_role

        with st.spinner("Scoring your resume..."):
            # Call Flask API
            try:
                files = {"resume": (uploaded_file.name, uploaded_file, "application/pdf")}
                data = {"job_role": actual_role}
                response = requests.post("http://127.0.0.1:5000/api/score", files=files, data=data)

                if response.status_code == 200:
                    result = response.json()

                    # Score display
                    score = result.get("score", 0)
                    suggestions = result.get("suggestions", [])
                    feedback = result.get("feedback", "")
                    courses = result.get("courses", [])

                    st.markdown(f'<div class="score-box"><h3>📊 Resume Match Score: {score}/100</h3></div>', unsafe_allow_html=True)
                    # Progress bar style
                    bar_width = min(max(score, 0), 100)
                    st.markdown(f'''
                        <div class="bar-container">
                            <div class="bar-fill" style="width:{bar_width}%;">{bar_width}%</div>
                        </div>
                    ''', unsafe_allow_html=True)

                    # Improvement checklist
                    st.markdown("### ✅ Improvement Suggestions")
                    if suggestions:
                        for s in suggestions:
                            st.markdown(f"- {s}")
                    else:
                        st.markdown("Your resume covers all the important skills!")

                    # Feedback section
                    st.markdown("### 💡 Personalized Feedback")
                    st.info(feedback)

                    # Recommended courses
                    if courses:
                        st.markdown("### 🎓 Recommended Skill Improvement Courses")
                        for course in courses:
                            st.markdown(f"- {course}")

                    # Skill breakdown chart (mocked here)
                    st.markdown("### 📈 Skill Match Breakdown")
                    skills = ["Core Skills", "Relevant Experience", "Education", "Certifications"]
                    # Dummy percentages for demo, ideally from backend
                    values = [score*0.7, score*0.2, score*0.1, score*0.05]

                    fig, ax = plt.subplots()
                    ax.barh(skills, values, color="#764ba2")
                    ax.set_xlim(0, 100)
                    ax.set_xlabel("Match Percentage")
                    st.pyplot(fig)

                else:
                    st.error(f"API Error: {response.json().get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"Failed to connect to backend API: {e}")
