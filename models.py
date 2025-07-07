from mongoengine import (Document, StringField, IntField, FloatField,
                         EmbeddedDocument, EmbeddedDocumentField, DateField, ListField, DateTimeField)
from datetime import datetime


class User(Document):
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
        }


class Contact1(EmbeddedDocument):
    phone = StringField()
    email = StringField()
    linkedin = StringField()
    github = StringField()
    leetcode = StringField()

    def to_json(self):
        return {
            "phone": self.phone,
            "email": self.email,
            "linkedin": self.linkedin,
            "github": self.github,
            "leetcode": self.leetcode
        }


class Education(EmbeddedDocument):
    degree = StringField()
    university = StringField()
    location = StringField()
    start_year = StringField()
    end_year = StringField()
    cgpa = FloatField()
    grade = StringField()
    description = StringField()

    def to_json(self):
        return {
            "degree": self.degree,
            "university": self.university,
            "location": self.location,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "cgpa": self.cgpa,
            "grade": self.grade,
            "description": self.description
        }


class Projects(EmbeddedDocument):
    title = StringField()
    description = StringField()
    link = StringField()

    def to_json(self):
        return {
            "title": self.title,
            "description": self.description,
            "link": self.link
        }


class Experience(EmbeddedDocument):
    title = StringField()
    company = StringField()
    location = StringField()
    description = StringField()
    from_date = StringField()
    to_date = StringField()

    def to_json(self):
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "from_date": self.from_date,
            "to_date": self.to_date
        }


class Activity(EmbeddedDocument):
    title = StringField()
    duration = StringField()

    def to_json(self):
        return {
            "title": self.title,
            "duration": self.duration
        }


class Skill(EmbeddedDocument):
    name = StringField(required=True)
    level = StringField()

    def to_json(self):
        return {
            "name": self.name,
            "level": self.level
        }


class FreshmanResume(Document):
    name = StringField(required=True)
    template = IntField(default=1)
    timestamp = DateTimeField(default=datetime.utcnow, required=True)
    contact = EmbeddedDocumentField(Contact1)
    objective = StringField()
    education = ListField(EmbeddedDocumentField(Education))
    project = ListField(EmbeddedDocumentField(Projects))
    experience = ListField(EmbeddedDocumentField(Experience))
    skills = StringField()
    summary = StringField()
    activities = ListField(EmbeddedDocumentField(Activity))

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "contact1": self.contact.to_json(),
            "objective": self.objective,
            "education": [edu.to_json() for edu in self.education],
            "project": [proj.to_json() for proj in self.project],
            "experience": [exp.to_json() for exp in self.experience],
            "skills": self.skills,
            "summary": self.summary,
            "activities": [act.to_json() for act in self.activities],
            "template": self.template,
            "timestamp": self.timestamp.isoformat()
        }


class Interest(EmbeddedDocument):
    title = StringField()


class JohnResume(Document):
    template = IntField(default=2)
    timestamp = DateTimeField(default=datetime.utcnow)
    name = StringField()
    email = StringField()
    phone = StringField()
    job = StringField()
    jdescription = StringField()
    objective = StringField()
    experience = ListField(EmbeddedDocumentField(Experience))
    education = ListField(EmbeddedDocumentField(Education))
    project = ListField(EmbeddedDocumentField(Projects))
    skill = ListField(EmbeddedDocumentField(Skill))
    interest = ListField(EmbeddedDocumentField(Interest))

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "job": self.job,
            "jdescription": self.jdescription,
            "objective": self.objective,
            "experience": [exp.to_json() for exp in self.experience],
            "education": [edu.to_json() for edu in self.education],
            "project": [proj.to_json() for proj in self.project],
            "skill": [s.to_json() for s in self.skill],
            "interest": [intr.to_json() for intr in self.interest],
            "template": self.template,
            "timestamp": self.timestamp.isoformat()

        }


class CampbellResume(Document):
    template = IntField(default=3)
    timestamp = DateTimeField(default=datetime.utcnow)
    prof = StringField()
    fname = StringField()
    lname = StringField()
    email = StringField()
    phone = StringField()
    address = StringField()
    website = StringField()
    objective = StringField()
    dob = StringField()
    nationality = StringField()
    experience = ListField(EmbeddedDocumentField(Experience))
    education = ListField(EmbeddedDocumentField(Education))
    skill = ListField(EmbeddedDocumentField(Skill))
    languages = ListField(EmbeddedDocumentField(Skill))

    def to_json(self):
        return {
            "id": str(self.id),
            "prof": self.prof,
            "fname": self.fname,
            "lname": self.lname,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "website": self.website,
            "objective": self.objective,
            "dob": self.dob,
            "nationality": self.nationality,
            "experience": [exp.to_json() for exp in self.experience],
            "education": [edu.to_json() for edu in self.education],
            "skill": [s.to_json() for s in self.skill],
            "languages": [l.to_json() for l in self.languages],
            "template": self.template,
            "timestamp": self.timestamp.isoformat()
        }
