import fitz  # PyMuPDF
import re
from sentence_transformers import SentenceTransformer, util
import torch

model = SentenceTransformer("all-MiniLM-L6-v2")

# Predefined skills list
skills_list = [
    "Python", "Java", "JavaScript", "C++", "C#", "SQL",
    "React", "Angular", "Node.js", "Django", "HTML/CSS", "REST API",
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQLite",
    "AWS", "Azure", "Docker", "Kubernetes", "Git", "CI/CD",
    "Machine Learning", "Data Analysis", "TensorFlow", "PyTorch" ,"Pandas", "Statistics", "Power BI",
    "Microsoft Office", "Excel", "SharePoint", ".NET", "SQL Server",
    "Project Management", "Team Leadership", "Agile", "Scrum", "Strategic Planning", "Budget Management",
    "Business Analysis", "Communication", "Customer Service", "Market", "CRM",
    "Software Testing", "Test Automation", "Selenium", "Quality Assurance",
    "Cybersecurity", "Information Security", "Network Security", "Data Security",
    "UI/UX Design", "User Experience", "Figma", "Adobe Creative Suite", "Wireframing", "Prototyping",
    "iOS Development", "Android Development", "React Native", "Flutter", "Swift", "Mobile App Development"
]

def extract_skills_from_pdf(pdf_path, threshold=0.65):
    resume_text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            resume_text += page.get_text() + "\n"

    words = list(set(re.findall(r'\b[A-Za-z][A-Za-z0-9\+\#\/\.\-]{1,30}\b', resume_text)))

    if not words:
        return []

    resume_embeddings = model.encode(words, convert_to_tensor=True)
    skills_embeddings = model.encode(skills_list, convert_to_tensor=True)

    extracted_skills = []

    for i, word_embedding in enumerate(resume_embeddings):
        similarities = util.pytorch_cos_sim(word_embedding, skills_embeddings)[0]
        if torch.max(similarities) >= threshold:
            extracted_skills.append(words[i])

    return sorted(set(extracted_skills))


