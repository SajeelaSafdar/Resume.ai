from sentence_transformers import SentenceTransformer, util
import pandas as pd

model = None
jobs = []

def load_jobs(file_path="jobs.csv"):
    """Load jobs from single CSV file containing all companies"""
    jobs = []
    try:
        df = pd.read_csv(file_path)
        
        # CSV structure: Job Title, Job URL, Source
        for _, row in df.iterrows():
            title = row['Job Title']
            link = row['Job URL'] 
            jobs.append((title.strip(), link.strip()))
            
        print(f"Loaded {len(jobs)} jobs from all companies: {file_path}")
    except Exception as e:
        print(f"Error loading jobs from CSV: {e}")
        print("Please check if the jobs.csv file exists and has the correct column names")
    return jobs

def initialize():
    """Initialize model and jobs"""
    global model, jobs
    try:
        model = SentenceTransformer("fine_tuned_model")
        jobs = load_jobs("jobs.csv")
        print(f"Loaded {len(jobs)} jobs from all companies and model successfully")
    except Exception as e:
        print(f"Error loading model/jobs: {e}")

def get_job_recommendations(skills, top_n=10):
    """Get job recommendations based on skills from all companies"""
    global model, jobs
    
    if not model or not jobs:
        return []
    
    try:
        job_titles = [title for title, _ in jobs]
        job_embeddings = model.encode(job_titles, convert_to_tensor=True)
        skill_query = " ".join(skills)
        skill_embedding = model.encode(skill_query, convert_to_tensor=True)
        similarities = util.cos_sim(skill_embedding, job_embeddings)[0]
        top_results = similarities.argsort(descending=True)[:top_n]
        
        recommendations = []
        for idx in top_results:
            title, link = jobs[int(idx)]
            score = similarities[int(idx)].item()
            recommendations.append({
                'title': title,
                'link': link,
                'score': score
            })
        
        return recommendations
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return []

initialize()