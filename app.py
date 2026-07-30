from flask import Flask, render_template, request
import os
import pdfplumber

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Technical skills list
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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "resume" not in request.files:
        return "No file uploaded."

    file = request.files["resume"]

    if file.filename == "":
        return "Please select a PDF."

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Extract text
    text = ""

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

    # Detect skills
    found_skills = []

    for skill in SKILLS:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    # ATS Score
    score = 0

    if "email" in text.lower():
        score += 5

    if "phone" in text.lower():
        score += 5

    if "summary" in text.lower():
        score += 10

    if "education" in text.lower():
        score += 10

    score += min(len(found_skills), 20)

    if "project" in text.lower():
        score += 20

    if "internship" in text.lower() or "experience" in text.lower():
        score += 20

    if "certification" in text.lower():
        score += 10

    score = min(score, 100)

    # Suggestions
    suggestions = []

    if score < 80:
        suggestions.append("Add more technical skills.")

    if "certification" not in text.lower():
        suggestions.append("Add certifications.")

    if "project" not in text.lower():
        suggestions.append("Include at least 2-3 projects.")

    if "internship" not in text.lower() and "experience" not in text.lower():
        suggestions.append("Add internship or work experience.")

    if len(found_skills) < 8:
        suggestions.append("Include more programming skills.")

    if "github" not in text.lower():
        suggestions.append("Add your GitHub profile.")

    if "linkedin" not in text.lower():
        suggestions.append("Add your LinkedIn profile.")

    return render_template(
        "result.html",
        resume_text=text,
        skills=found_skills,
        score=score,
        suggestions=suggestions
    )


if __name__ == "__main__":
    app.run(debug=True)