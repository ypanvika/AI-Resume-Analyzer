from flask import Flask, render_template, request
import os
import re
import pdfplumber

app = Flask(__name__)

# ---------------- Upload Folder ---------------- #

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- Technical Skills ---------------- #

SKILLS = [
    "Python", "Java", "C", "C++", "SQL",
    "HTML", "CSS", "JavaScript",
    "Flask", "Django", "React", "Node.js",
    "Git", "GitHub",
    "MySQL", "PostgreSQL", "MongoDB",
    "Machine Learning", "Deep Learning",
    "Data Analysis", "Pandas", "NumPy",
    "Scikit-learn", "TensorFlow",
    "Data Structures", "Algorithms",
    "DBMS", "Operating Systems", "OOP"
]

# ---------------- ATS Score ---------------- #

def calculate_ats_score(text):

    score = 0

    found_skills = []

    for skill in SKILLS:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    # Skill Score (Max 50)
    score += min(len(found_skills) * 5, 50)

    # Resume Length (Max 20)

    words = len(text.split())

    if words >= 300:
        score += 20
    elif words >= 200:
        score += 15
    elif words >= 100:
        score += 10

    # Email & Phone (15)

    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
        score += 8

    if re.search(r"(\+?\d[\d\s-]{8,}\d)", text):
        score += 7

    # Education (15)

    education_keywords = [
        "b.tech",
        "bachelor",
        "master",
        "college",
        "university",
        "degree"
    ]

    if any(word in text.lower() for word in education_keywords):
        score += 15

    return min(score, 100), found_skills


# ---------------- Home Page ---------------- #

@app.route("/")
def index():
    return render_template("index.html")


# ---------------- Upload Resume ---------------- #

@app.route("/upload", methods=["POST"])
def upload():

    if "resume" not in request.files:
        return "No file uploaded."

    file = request.files["resume"]

    if file.filename == "":
        return "Please select a PDF."

    if not file.filename.lower().endswith(".pdf"):
        return "Only PDF files are allowed."

    job_description = request.form.get(
        "job_description", ""
    ).strip()

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    text = ""

    with pdfplumber.open(filepath) as pdf:

        for page in pdf.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"
      # ---------------- ATS Score ---------------- #

    score, found_skills = calculate_ats_score(text)

    # ---------------- Candidate Information ---------------- #

    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    email = email_match.group() if email_match else "Not Found"

    phone_match = re.search(
        r"(\+?\d[\d\s-]{8,}\d)",
        text
    )

    phone = phone_match.group() if phone_match else "Not Found"

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    if len(lines) > 0:
        name = lines[0]
    else:
        name = "Not Found"

    # ---------------- Resume Suggestions ---------------- #

    suggestions = []

    if len(found_skills) < 8:
        suggestions.append("Add more technical skills.")

    if "project" not in text.lower():
        suggestions.append("Include 2-3 projects.")

    if "internship" not in text.lower() and "experience" not in text.lower():
        suggestions.append("Add internship or work experience.")

    if "certification" not in text.lower():
        suggestions.append("Add certifications.")

    if "github" not in text.lower():
        suggestions.append("Add your GitHub profile.")

    if "linkedin" not in text.lower():
        suggestions.append("Add your LinkedIn profile.")

    if score < 80:
        suggestions.append("Improve ATS score by adding more keywords.")

    # ---------------- Job Description Matching ---------------- #

    matched_skills = []
    missing_skills = []
    match_score = 0

    if job_description:

        jd_lower = job_description.lower()

        jd_skills = []

        for skill in SKILLS:
            if skill.lower() in jd_lower:
                jd_skills.append(skill)

        for skill in jd_skills:

            if skill in found_skills:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        if len(jd_skills) > 0:
            match_score = int(
                (len(matched_skills) / len(jd_skills)) * 100
            )
        else:
            match_score = 100       
    # ---------------- Display Result ---------------- #

    return render_template(
        "result.html",
        resume_text=text,
        score=score,
        skills=found_skills,
        suggestions=suggestions,
        match_score=match_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        name=name,
        email=email,
        phone=phone
    )


# ---------------- Run Flask ---------------- #

if __name__ == "__main__":
    app.run(debug=True)       