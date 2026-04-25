from typing import List

from app.schemas.job import JobProfile
import re

class Jd_understanding_agent:
    def __init__(self) -> None:
        self.skill_keywords = [
            "python",
            "java",
            "sql",
            "pytorch",
            "tensorflow",
            "machine learning",
            "deep learning",
            "nlp",
            "transformers",
            "bert",
            "llm",
            "rag",
            "langchain",
            "fastapi",
            "docker",
            "aws",
            "git",
            "pandas",
            "numpy",
            "scikit-learn"
        ]
        self.education_keywords = [
            "computer science",
            "artificial intelligence",
            "data science",
            "software engineering",
            "engineering",
        ]
        self.default_weights = {
            "skills" : 0.4,
            "experience" : 0.2,
            "projects" : 0.3,
            "education" : 0.1,
            "bonus" : 0.1

        }

    def run(self,job_texts:str) -> JobProfile:
        cleaned_text = self.clean_text(job_texts)
        title = self.extract_must_have_text(cleaned_text)
        must_have_skills = self.extract_must_have_skills(cleaned_text)
        nice_to_have_skills = self.extract_nice_to_have_skills(cleaned_text)
        min_years_experience = self.extract_min_years_experience(cleaned_text)
        education_requirement = self.extract_education_requirements(cleaned_text)

        return JobProfile(
            title=title,
            must_have_skills=must_have_skills,
            nice_to_have_skills=nice_to_have_skills,
            min_years_experience=min_years_experience,
            education_requirements=education_requirement,
            weights=self.default_weights

        )

    def clean_text(self,text:str)->str:
        text = text.lower().strip()
        text = re.sub(r"\s+"," ",text)
        return text

    def extract_must_have_text(self,text:str)->str:
        patterns = [
            r"(?:hiring for|looking for|seeking|position:|role:)\s+([a-zA-Z0-9 /\-]+)",
            r"([a-zA-Z0-9 /\-]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern,text)
            if match:
                title = match.group(1).strip(" .:-")
                return title.title()

        return "Unknown Role"

    def extract_must_have_skills(self,text:str):
        must_have_marks = [
            "must have",
            "requirements",
            "required",
            "must be qualified with",
            "qualification",
            "qualifications"
        ]
        collection = []

        for mark in must_have_marks:
            if mark in text:
                index = text.find(mark)
                relevant_text = text[index:]
                found_must_skills = self.find_skills_in_text(relevant_text)
                collection.extend(found_must_skills)

        return self.deduplicate(collection)



    def extract_nice_to_have_skills(self,text:str)->List[str]:
        nice_marks = [
            "nice to have",
            "preferred",
            "bonus",
            "plus",
            "preferred qualification"
        ]

        collection = []
        for mark in nice_marks:
            if mark in text:
                index = text.find(mark)
                relevant_text = text[index:]
                found_nice_skills = self.find_skills_in_text(relevant_text)
                collection.extend(found_nice_skills)


        return self.deduplicate(collection)

    def extract_min_years_experience(self,text:str)->float:
        patterns =[
            r"(\d+(?:\.\d+)?)\+?\s+years? of experience",
            r"minimum of (\d+(?:\.\d+)?)\+?\s+years?",
            r"at least (\d+(?:\.\d+)?)\+?\s+years?",
        ]

        for pattern in patterns:
            match = re.search(pattern,text)
            if match:
                experience_years = match.group(1)
                return float(experience_years)

        return None

    def extract_education_requirements(self,text:str):
        collection = []
        for requirement in self.education_keywords:
            if requirement in text:
                collection.append(requirement.title())

        return self.deduplicate(collection)

    def find_skills_in_text(self,text:str)->List[str]:
        collection = []
        for skill in self.skill_keywords:
            pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern,text):
                collection.append(skill.title())

        return self.deduplicate(collection)

    def deduplicate(self,items:List[str])->List[str]:
        seen = set()
        result = []
        for item in items:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                result.append(item)

        return result











