# Automated Resume Screener & Skill-Matcher

## Project Overview

Automated Resume Screener & Skill-Matcher is a web-based application that helps analyze resumes and compare candidate skills with the requirements of a job description.

The system extracts information from a PDF resume, identifies technical skills, calculates a job match score, shows matched and missing skills, and provides a candidate recommendation.

## Features

- Upload PDF resumes
- Extract resume text automatically
- Extract candidate name, email, and phone number
- Detect technical skills
- Compare resume skills with job requirements
- Calculate candidate match score
- Display matched skills
- Display missing skills
- Provide candidate recommendation
- Generate downloadable PDF screening reports
- User-friendly web interface
- Basic error handling

## Technologies Used

- Python
- Flask
- HTML
- CSS
- PyMuPDF
- ReportLab

## Project Structure

```text
automated-resume-screener/
│
├── app.py
├── requirements.txt
├── README.md
│
├── uploads/
│
├── templates/
│   ├── index.html
│   ├── result.html
│   └── error.html
│
└── static/
    └── style.css