def calculate_score(resume_data, job_data):
    """
    Calculate match score between a parsed resume and a job description.
    
    :param resume_data: Dictionary containing resume details (skills, experience, education).
    :param job_data: Dictionary containing job requirements (skills, min_experience, education).
    :return: Match score (0-100).
    """
    resume_skills = set(resume_data.get("skills", []))
    job_skills = set(job_data.get("skills", []))

    # Skill match percentage (50% weightage)
    skill_match = (len(resume_skills & job_skills) / len(job_skills) * 50) if job_skills else 0  

    # Experience match (30% weightage) - Capped at 30
    resume_exp = resume_data.get("experience", 0)
    job_exp = job_data.get("min_experience", 1)
    experience_match = min(resume_exp / job_exp, 1) * 30  # Normalized match

    # Education match (20% weightage) - Improved partial matching
    education_match = 0  
    if resume_data.get("education") and job_data.get("education"):
        if resume_data["education"].lower() in job_data["education"].lower():
            education_match = 20  # Exact match
        elif "bachelor" in resume_data["education"].lower() and "bachelor" in job_data["education"].lower():
            education_match = 15  # Partial match
        elif "master" in resume_data["education"].lower() and "master" in job_data["education"].lower():
            education_match = 15  # Partial match

    total_score = skill_match + experience_match + education_match
    return round(total_score, 2)

# Example usage
if __name__ == "__main__":
    sample_resume = {
        "skills": ["Python", "Machine Learning", "SQL"],
        "experience": 5,  # Higher than required
        "education": "B.Tech"
    }

    sample_job = {
        "skills": ["Python", "SQL", "Data Analysis"],
        "min_experience": 2,
        "education": "Bachelor's"
    }

    print("Match Score:", calculate_score(sample_resume, sample_job))
