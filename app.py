from flask import Flask, render_template, request, send_file
import os
import fitz
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# SKILL DATABASE
# =========================================================

SKILLS = [

    # Programming Languages
    "C",
    "C++",
    "Java",
    "Python",
    "JavaScript",
    "TypeScript",
    "PHP",
    "Ruby",
    "Go",
    "Kotlin",
    "Swift",

    # Web Development
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Express",
    "Bootstrap",
    "Tailwind",

    # Backend / Frameworks
    "Flask",
    "Django",
    "Spring",
    "Spring Boot",
    "Laravel",

    # Databases
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "SQLite",
    "Oracle",

    # Cloud
    "AWS",
    "Microsoft Azure",
    "Google Cloud",
    "Docker",
    "Kubernetes",

    # Data / AI
    "Machine Learning",
    "Deep Learning",
    "Data Science",
    "Artificial Intelligence",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",

    # Cybersecurity
    "Cybersecurity",
    "Ethical Hacking",
    "Penetration Testing",
    "Network Security",
    "Cryptography",

    # Tools
    "Git",
    "GitHub",
    "GitLab",
    "Linux",
    "Jenkins",
    "Postman"
]


# =========================================================
# FIND SKILLS
# =========================================================

def find_skills(text):

    found_skills = []

    for skill in SKILLS:

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills


# =========================================================
# EXTRACT CANDIDATE INFORMATION
# =========================================================

def extract_candidate_info(text):

    # Extract email
    email_match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )

    email = (
        email_match.group(0)
        if email_match
        else "Not found"
    )


    # Extract phone number
    phone_match = re.search(
        r'(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}',
        text
    )

    phone = (
        phone_match.group(0)
        if phone_match
        else "Not found"
    )


    # Extract candidate name
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    name = "Not found"

    if lines:

        first_line = lines[0]

        if len(first_line.split()) <= 5:
            name = first_line


    return name, email, phone


# =========================================================
# MATCH SKILLS AND CALCULATE SCORE
# =========================================================

def match_skills(resume_text, job_description):

    resume_skills = find_skills(resume_text)

    job_skills = find_skills(job_description)

    matched_skills = []
    missing_skills = []


    # Compare required skills with resume skills
    for skill in job_skills:

        if skill in resume_skills:

            matched_skills.append(skill)

        else:

            missing_skills.append(skill)


    # Calculate skill match score
    if len(job_skills) > 0:

        skill_score = (
            len(matched_skills) /
            len(job_skills)
        ) * 100

    else:

        skill_score = 0


    # Calculate resume content score
    resume_words = len(resume_text.split())


    if resume_words >= 300:

        content_score = 100

    elif resume_words >= 150:

        content_score = 80

    elif resume_words >= 75:

        content_score = 60

    else:

        content_score = 40


    # Final score
    final_score = (
        (skill_score * 0.80) +
        (content_score * 0.20)
    )


    return (
        matched_skills,
        missing_skills,
        round(final_score, 2)
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# UPLOAD AND ANALYZE RESUME
# =========================================================

@app.route("/upload", methods=["POST"])
def upload_resume():

    # Get job description
    job_description = request.form.get(
        "job_description",
        ""
    ).strip()


    # Check job description
    if not job_description:

        return render_template(
            "error.html",
            message="Please enter a job description."
        )


    # Check resume field
    if "resume" not in request.files:

        return render_template(
            "error.html",
            message="Please select a resume PDF."
        )


    resume = request.files["resume"]


    # Check filename
    if resume.filename == "":

        return render_template(
            "error.html",
            message="No resume was selected."
        )


    # Check file type
    if not resume.filename.lower().endswith(".pdf"):

        return render_template(
            "error.html",
            message="Only PDF files are allowed."
        )


    # Save resume
    filename = resume.filename

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    resume.save(file_path)


    # Check that file was saved
    if not os.path.exists(file_path):

        return render_template(
            "error.html",
            message="The resume could not be saved."
        )


    # =====================================================
    # EXTRACT TEXT FROM PDF
    # =====================================================

    try:

        document = fitz.open(file_path)

        text = ""

        for page in document:

            text += page.get_text()

        document.close()


    except Exception:

        return render_template(
            "error.html",
            message="The uploaded PDF could not be read. Please try another PDF resume."
        )


    # Check whether PDF contains text
    if not text.strip():

        return render_template(
            "error.html",
            message="No readable text was found in this PDF."
        )


    # =====================================================
    # FIND RESUME SKILLS
    # =====================================================

    found_skills = find_skills(text)


    # =====================================================
    # EXTRACT CANDIDATE INFORMATION
    # =====================================================

    candidate_name, email, phone = extract_candidate_info(
        text
    )


    # =====================================================
    # MATCH SKILLS
    # =====================================================

    (
        matched_skills,
        missing_skills,
        match_percentage
    ) = match_skills(
        text,
        job_description
    )


    # =====================================================
    # RECOMMENDATION
    # =====================================================

    if match_percentage >= 80:

        recommendation = "Strong Match"

    elif match_percentage >= 60:

        recommendation = "Good Match"

    elif match_percentage >= 40:

        recommendation = "Moderate Match"

    else:

        recommendation = "Low Match"


    # =====================================================
    # SHOW RESULT
    # =====================================================

    return render_template(
        "result.html",

        text=text,

        skills=found_skills,

        matched_skills=matched_skills,

        missing_skills=missing_skills,

        match_percentage=match_percentage,

        recommendation=recommendation,

        candidate_name=candidate_name,

        email=email,

        phone=phone
    )


# =========================================================
# CREATE PDF REPORT
# =========================================================

def create_report(
    name,
    email,
    phone,
    score,
    recommendation,
    matched_skills,
    missing_skills
):

    from reportlab.lib.pagesizes import A4

    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer
    )

    from reportlab.lib.styles import (
        getSampleStyleSheet
    )


    report_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "resume_analysis_report.pdf"
    )


    styles = getSampleStyleSheet()


    document = SimpleDocTemplate(
        report_path,
        pagesize=A4
    )


    content = []


    # Title
    content.append(
        Paragraph(
            "RESUME SCREENING REPORT",
            styles["Title"]
        )
    )


    content.append(
        Spacer(1, 20)
    )


    # Candidate information
    content.append(
        Paragraph(
            f"<b>Candidate Name:</b> {name}",
            styles["Normal"]
        )
    )


    content.append(
        Paragraph(
            f"<b>Email:</b> {email}",
            styles["Normal"]
        )
    )


    content.append(
        Paragraph(
            f"<b>Phone:</b> {phone}",
            styles["Normal"]
        )
    )


    content.append(
        Spacer(1, 15)
    )


    # Score
    content.append(
        Paragraph(
            f"<b>Match Score:</b> {score}%",
            styles["Normal"]
        )
    )


    content.append(
        Paragraph(
            f"<b>Recommendation:</b> {recommendation}",
            styles["Normal"]
        )
    )


    content.append(
        Spacer(1, 20)
    )


    # Matched skills
    content.append(
        Paragraph(
            "Matched Skills",
            styles["Heading2"]
        )
    )


    if matched_skills:

        for skill in matched_skills:

            content.append(
                Paragraph(
                    f"✓ {skill}",
                    styles["Normal"]
                )
            )

    else:

        content.append(
            Paragraph(
                "No matched skills.",
                styles["Normal"]
            )
        )


    content.append(
        Spacer(1, 20)
    )


    # Missing skills
    content.append(
        Paragraph(
            "Missing Skills",
            styles["Heading2"]
        )
    )


    if missing_skills:

        for skill in missing_skills:

            content.append(
                Paragraph(
                    f"! {skill}",
                    styles["Normal"]
                )
            )

    else:

        content.append(
            Paragraph(
                "No missing skills.",
                styles["Normal"]
            )
        )


    # Build PDF
    document.build(content)


    return report_path


# =========================================================
# DOWNLOAD PDF REPORT
# =========================================================

@app.route("/download_report")
def download_report():

    name = request.args.get(
        "name",
        "Not found"
    )

    email = request.args.get(
        "email",
        "Not found"
    )

    phone = request.args.get(
        "phone",
        "Not found"
    )

    score = request.args.get(
        "score",
        "0"
    )

    recommendation = request.args.get(
        "recommendation",
        "Not available"
    )


    matched = request.args.get(
        "matched",
        ""
    )

    missing = request.args.get(
        "missing",
        ""
    )


    matched_skills = (
        matched.split(",")
        if matched
        else []
    )


    missing_skills = (
        missing.split(",")
        if missing
        else []
    )


    # Create report
    report_path = create_report(
        name,
        email,
        phone,
        score,
        recommendation,
        matched_skills,
        missing_skills
    )


    # Send PDF to user
    return send_file(
        report_path,
        as_attachment=True,
        download_name="Resume_Screening_Report.pdf"
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)