import os
import streamlit as st

# Page Configuration
st.set_page_config(page_title="RESUME SCORER FOR IT JOB APPLICANTS", layout="wide")

# Get the absolute path of the asset folder
asset_path = os.path.join(os.path.dirname(__file__), "asset")

# Custom CSS for Styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');

        .stApp {
            background: linear-gradient(135deg, #001f3f, #0074D9);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .title-text {
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            text-transform: uppercase;
            font-family: 'Poppins', sans-serif;
            color: white;
            margin-bottom: 40px; /* Increased gap */
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }

        .title-icon {
            width: 50px;
            height: auto;
        }

        .how-it-works {
            text-align: center;
            font-size: 30px;
            font-weight: bold;
            color: white;
            margin-top: 50px; /* Added more gap after How It Works */
            margin-bottom: 30px; 
        }

        .how-it-works-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 40px; /* Increased gap between boxes */
            text-align: center;
            margin-top: 30px;
        }

        .how-it-works-box {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            width: 30%;
        }

        .upload-container {
            padding: 30px;
            text-align: left;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            width: 60%;
            margin-top: 50px; /* Increased gap */
        }

        .dropdown-label {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
            color: white;
        }

        .submit-btn {
            background-color: #6C63FF;
            color: white;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            margin-top: 20px; /* More spacing */
        }

        .left-container {
            width: 50%;
            padding-left: 10%;
        }
        
        .right-container img {
            width: 70%; /* Reduced size to zoom */
            height: auto;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }

    </style>
""", unsafe_allow_html=True)

# Title with Resume Icon
st.markdown("""
    <div class="title-text">
        RESUME SCORER FOR IT JOB APPLICANTS
        <img src="https://cdn-icons-png.flaticon.com/512/2991/2991588.png" class="title-icon">
    </div>
""", unsafe_allow_html=True)

# Main Layout
col1, col2 = st.columns([1, 1])

# Left Side: Upload & Job Role Selection
with col1:
    st.markdown("<div class='left-container'>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Drop your resume here or choose a file", type=["pdf", "docx"])
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<span class='dropdown-label'>Select Job Role:</span>", unsafe_allow_html=True)
    job_roles = ["Select the Job Role", "Frontend Developer", "Prompt Engineer", "Backend Developer", "Python Developer", "Other"]
    selected_role = st.selectbox("", job_roles, index=0)

    if selected_role == "Other":
        custom_role = st.text_input("Enter your job role:")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Get Resume Score"):
        job_title = custom_role if selected_role == "Other" else selected_role
        if selected_role == "Select the Job Role":
            st.error("Please select a valid job role.")
        else:
            st.success(f"Resume uploaded successfully for {job_title}")

    st.markdown("</div>", unsafe_allow_html=True)

# Right Side: Resume Analysis Image
with col2:
    st.markdown("<div class='right-container'>", unsafe_allow_html=True)
    st.image(os.path.join(asset_path, "resume.jpg"), caption="Resume Analysis", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# How It Works Section (Now Below the Upload Section)
st.markdown("<h2 class='how-it-works'>How It Works</h2>", unsafe_allow_html=True)

# Create Three Columns for Steps
col1, col2, col3 = st.columns(3)

with col1:
    st.image(os.path.join(asset_path, "upload.jpg"), width=120)
    st.markdown("<h3 style='text-align:center;'>1. Upload your resume</h3>", unsafe_allow_html=True)
    st.write("<p style='text-align:center;'>Just upload your resume, no matter what state it is in.</p>", unsafe_allow_html=True)

with col2:
    st.image(os.path.join(asset_path, "score meter.jpeg"), width=120)
    st.markdown("<h3 style='text-align:center;'>2. Resume Scoring</h3>", unsafe_allow_html=True)
    st.write("<p style='text-align:center;'>Our algorithm scores your resume based on industry standards.</p>", unsafe_allow_html=True)

with col3:
    st.image(os.path.join(asset_path, "feedback 2.jpg"), width=120)
    st.markdown("<h3 style='text-align:center;'>3. Get Instant Feedback</h3>", unsafe_allow_html=True)
    st.write("<p style='text-align:center;'>Get a detailed report on how to improve your resume.</p>", unsafe_allow_html=True)
