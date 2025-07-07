from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from mongoengine import connect
from datetime import datetime
from flask_session import Session
from models import (User, Contact1, Education, Experience, Projects,
                    Activity, FreshmanResume, Skill, JohnResume, Interest, CampbellResume)
from job_recommender import get_job_recommendations
from skills_extractor import extract_skills_from_pdf
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object('config')
Session(app)
db = connect(db="resume", host="localhost", port=27017)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/signindb', methods=['POST'])
def signindb():
    try:

        email = request.form['email']
        password = request.form['password']
        user = User.objects(email=email, password=password).first()
        if user:
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('signin.html',
                                   error="No such user exists. If you don't have an account, please sign up.")
    except Exception as e:
        return render_template('signin.html', error=str(e))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signupdb', methods=['POST'])
def signupdb():
    try:
        name = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        user = User(name=name, email=email, password=password)
        user.save()
        session['user_email'] = email
        return redirect(url_for('dashboard'))
    except Exception as e:
        return render_template('signup.html', error=str(e))


@app.route('/templates')
def templates():
    return render_template('selectResume.html')


@app.route('/seetemplates')
def seetemplates():
    return render_template('seetemplates.html')


@app.route('/freshman')
def freshman():
    return render_template('freshmanForm.html')


@app.route('/john')
def john():
    return render_template('johnForm.html')


@app.route('/campbell')
def campbell():
    return render_template('campbellForm.html')


@app.route('/freshmandb', methods=['POST'])
def freshmandb():
    try:
        name = request.form['name']
        contact = Contact1(
            email=request.form['email'],
            phone=request.form['phone'],
            linkedin=request.form['linkedin'],
            github=request.form['github'],
            leetcode=request.form['leetcode']
        )
        objective = request.form['objective']
        degrees = request.form.getlist('degree[]')
        universities = request.form.getlist('university[]')
        locations = request.form.getlist('location[]')
        from_dates = request.form.getlist('from_date[]')
        to_dates = request.form.getlist('to_date[]')
        cgpas = request.form.getlist('cgpa[]')
        grades = request.form.getlist('grade[]')

        educations = []
        for degree, university, location, from_date, to_date, cgpa, grade in zip(
                degrees, universities, locations, from_dates, to_dates, cgpas, grades
        ):
            education = Education(
                degree=degree,
                university=university,
                location=location,
                start_year=from_date,
                end_year=to_date,
                cgpa=cgpa,
                grade=grade
            )
            educations.append(education)

        titles = request.form.getlist('title[]')
        plinks = request.form.getlist('plink[]')
        pdescriptions = request.form.getlist('pdescription[]')
        projects = []
        for title, link, description in zip(titles, plinks, pdescriptions):
            project = Projects(
                title=title,
                link=link,
                description=description
            )
            projects.append(project)
        jtitles = request.form.getlist('jtitle[]')
        jlocations = request.form.getlist('jlocation[]')
        companies = request.form.getlist('company[]')
        jdescriptions = request.form.getlist('jdescription[]')
        experiences = []
        for title, location, description, company in zip(jtitles, jlocations, companies, jdescriptions):
            experience = Experience(
                title=title,
                location=location,
                description=description,
                company=company
            )
            experiences.append(experience)
        skills = request.form['skill']
        atitles = request.form.getlist('atitle[]')
        durations = request.form.getlist('duration[]')
        activities = []
        for atitle, duration in zip(atitles, durations):
            activity = Activity(
                title=atitle,
                duration=duration
            )
            activities.append(activity)

        resume1 = FreshmanResume(name=name, contact=contact, education=educations, objective=objective, project=projects
                                 , experience=experiences, skills=skills, activities=activities)
        resume1.save()
        return jsonify({'message': 'Saved Successfully'}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error in Saving'}), 500


@app.route('/johndb', methods=['POST'])
def johndb():
    try:
        uname = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        job = request.form['job']
        jdescription = request.form['jdescription']
        objective = request.form['objective']

        # experience group
        titles = request.form.getlist('title[]')
        locations = request.form.getlist('location[]')
        companies = request.form.getlist('company[]')
        descriptions = request.form.getlist('description[]')
        from_dates = request.form.getlist('from_date[]')
        to_dates = request.form.getlist('to_date[]')
        experiences = []
        for title, location, description, company, from_date, to_date in \
                zip(titles, locations, companies, descriptions, from_dates, to_dates):
            experience = Experience(
                title=title,
                location=location,
                description=description,
                company=company,
                from_date=from_date,
                to_date=to_date
            )
            experiences.append(experience)

        # education group
        degrees = request.form.getlist('degree[]')
        universities = request.form.getlist('university[]')
        locations = request.form.getlist('elocation[]')
        from_es = request.form.getlist('from_e[]')
        to_es = request.form.getlist('to_e[]')
        descriptions = request.form.getlist('edescription[]')

        educations = []
        for degree, university, location, from_date, to_date, description in zip(
                degrees, universities, locations, from_es, to_es, descriptions
        ):
            education = Education(
                degree=degree,
                university=university,
                location=location,
                start_year=from_date,
                end_year=to_date,
                description=description
            )
            educations.append(education)

        # projects group
        ptitles = request.form.getlist('ptitle[]')
        pdescriptions = request.form.getlist('pdescription[]')
        projects = []
        for title, description in zip(ptitles, pdescriptions):
            project = Projects(
                title=title,
                description=description
            )
            projects.append(project)

        # skills group
        snames = request.form.getlist('sname[]')
        slevels = request.form.getlist('sprof[]')
        skills = []
        for name, level in zip(snames, slevels):
            skill = Skill(
                name=name,
                level=level
            )
            skills.append(skill)
        ints = request.form.getlist('interest[]')
        interests = []
        for int in ints:
            interest = Interest(
                title=int
            )
            interests.append(interest)

        resume2 = JohnResume(name=uname, email=email, phone=phone, job=job, jdescription=jdescription,
                             objective=objective, education=educations, experience=experiences,
                             skill=skills, project=projects, interest=interests)
        resume2.save()
        return jsonify({'message': 'Saved Successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error in Saving'}), 500


@app.route('/campbelldb', methods=['POST'])
def campbelldb():
    try:
        prof = request.form['prof']
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']
        dob = request.form['dob']
        nationality = request.form['nationality']
        website = request.form['website']
        objective = request.form['objective']

        # experience group
        titles = request.form.getlist('title[]')
        locations = request.form.getlist('location[]')
        companies = request.form.getlist('company[]')
        descriptions = request.form.getlist('description[]')
        from_dates = request.form.getlist('from_date[]')
        to_dates = request.form.getlist('to_date[]')
        experiences = []
        for (title, location, description, company, from_date, to_date) in \
                zip(titles, locations, companies, descriptions, from_dates, to_dates):
            experience = Experience(
                title=title,
                location=location,
                description=description,
                company=company,
                from_date=from_date,
                to_date=to_date
            )
            experiences.append(experience)

        # education group
        degrees = request.form.getlist('degree[]')
        universities = request.form.getlist('university[]')
        locations = request.form.getlist('elocation[]')
        from_es = request.form.getlist('from_e[]')
        to_es = request.form.getlist('to_e[]')
        descriptions = request.form.getlist('edescription[]')

        educations = []
        for degree, university, location, from_date, to_date, description in zip(
                degrees, universities, locations, from_es, to_es, descriptions
        ):
            education = Education(
                degree=degree,
                university=university,
                location=location,
                start_year=from_date,
                end_year=to_date,
                description=description
            )
            educations.append(education)
        # languages group
        lang = request.form.getlist('language[]')
        lang_levels = request.form.getlist('lang_level[]')
        languages = []
        for l, level in zip(lang, lang_levels):
            language = Skill(
                name=l,
                level=level
            )
            languages.append(language)
        # skills group
        snames = request.form.getlist('sname[]')
        slevels = request.form.getlist('sdescription[]')
        skills = []
        for name, level in zip(snames, slevels):
            skill = Skill(
                name=name,
                level=level
            )
            skills.append(skill)
        resume3 = CampbellResume(prof=prof, fname=fname, lname=lname, email=email, address=address, phone=phone,
                                 dob=dob, nationality=nationality, website=website, objective=objective,
                                 education=educations, experience=experiences, skill=skills, languages=languages)
        resume3.save()
        return jsonify({'message': 'Saved Successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error in Saving'}), 500


@app.route('/logout')
def logout():
    session.clear()
    return render_template("home.html")


# helper function
def api_resumes():
    email = session.get('user_email')
    try:
        user = User.objects(email=email).only('name').first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        template1_resumes = FreshmanResume.objects(contact__email=email)
        template2_resumes = JohnResume.objects(email=email)
        template3_resumes = CampbellResume.objects(email=email)

        all_resumes = []

        for resume in template1_resumes:
            resume_data = resume.to_json()
            resume_data['template'] = 1
            resume_data["_id"] = str(resume_data["id"])
            all_resumes.append({
                "id": resume_data["id"],
                "template": 1,
                "created_at": resume_data["timestamp"],
                "data": resume_data
            })

        for resume in template2_resumes:
            resume_data = resume.to_json()
            resume_data['template'] = 2
            resume_data["_id"] = str(resume_data["id"])
            all_resumes.append({
                "id": resume_data["id"],
                "template": 2,
                "created_at": resume_data["timestamp"],
                "data": resume_data
            })

        for resume in template3_resumes:
            resume_data = resume.to_json()
            resume_data['template'] = 3
            resume_data["_id"] = str(resume_data["id"])
            all_resumes.append({
                "id": resume_data["id"],
                "template": 3,
                "created_at": resume_data["timestamp"],
                "data": resume_data
            })

        all_resumes.sort(key=lambda x: x["data"].get('timestamp', datetime.min), reverse=True)

        return all_resumes

    except Exception as e:
        print(f"Error in /api/resumes: {str(e)}")
        return jsonify({"error": "Server error"}), 500


@app.route('/dashboard')
def dashboard():
    user = User.objects(email=session.get('user_email')).only('name').first()
    resumes = api_resumes()
    return render_template('user.html', user_name=user.name, resumes_data=resumes)


@app.route('/api/resumes')
def apiresumes():
    email = session.get('user_email')
    return jsonify(api_resumes())

@app.route('/resume/edit/<resume_id>')
def edit(resume_id):
    template = request.args.get('template')
    if template == "1":
        resume = FreshmanResume.objects(id=resume_id).first()
    elif template == "2":
        resume = JohnResume.objects(id=resume_id).first()
    elif template == "3":
        resume = CampbellResume.objects(id=resume_id).first()
    else:
        return "Invalid template", 400

    if not resume:
        return "Resume not found", 404
    print(resume)
    if template == "1":
        resume_data = resume.to_mongo().to_dict()
        return render_template('freshmanForm.html',resume_data=resume)
    elif template == "3":
        resume_data = resume.to_mongo().to_dict()
        return render_template('campbellForm.html',resume_data=resume)
    elif template == "2":
        resume_data = resume.to_mongo().to_dict()
        return render_template('johnForm.html',resume_data=resume)

@app.route('/findJob')
def findJob():
    return render_template('findJob.html')

@app.route('/recommend-jobs', methods=['POST'])
def recommend_jobs():
    """Get job recommendations based on skills"""
    try:
        data = request.json
        skills = data.get('skills', [])
        
        if not skills:
            return jsonify([])
        
        recommendations = get_job_recommendations(skills)
        return jsonify(recommendations)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])
    
@app.route("/extract_skills", methods=["POST"])
def extract_skills():
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume_file = request.files["resume"]
    
    if resume_file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    temp_path = None
    try:
        filename = secure_filename(resume_file.filename)
        
        temp_path = f"temp_{filename}"
        
        resume_file.save(temp_path)
        
        extracted_skills = extract_skills_from_pdf(temp_path)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            "skills": extracted_skills,
            "message": f"Successfully extracted {len(extracted_skills)} skills"
        })
        
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error in extract_skills: {str(e)}") 
        return jsonify({"error": f"Failed to process resume: {str(e)}"}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
