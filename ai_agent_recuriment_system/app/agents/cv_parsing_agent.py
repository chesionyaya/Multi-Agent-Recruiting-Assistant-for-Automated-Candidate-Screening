import re
from typing import List
from app.schemas.candidate import Candidate_Profile, Experience_Item, Project_Item


class CV_parsing_agent():
    def __init__(self):
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
            "scikit-learn",
            "faiss",
            "networkx",
            "spacy",
        ]

        self.section_aliases = {
            "skills": ["skills", "technical skills", "tech stack"],
            "education": ["education", "academic background"],
            "experience": ["experience", "work experience", "professional experience","internship"],
            "projects": ["projects", "project experience", "academic projects"],
        }

    def run(self, cv_text: str) -> Candidate_Profile:
        cleaned_text = self.clean_text(cv_text)
        return Candidate_Profile(
            name=self.extract_name(cleaned_text),
            skills=self.extract_skills(cleaned_text),
            education=self.extract_educations(cleaned_text),
            experience=self.extract_experience(cleaned_text),
            project_experience=self.extract_project_experience(cleaned_text),
            raw_text=cleaned_text,
        )

    def clean_text(self, text: str) -> str:
        text = text.strip().lower()
        # Keep line boundaries for section parsing while normalizing whitespace.
        lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
        return "\n".join(lines)

    def extract_name(self, text: str) -> str | None:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return None

        first_line = lines[0]
        if len(first_line.split()) <= 5 and not any(char.isdigit() for char in first_line):
            return first_line.title()

        return None

    def extract_skills(self, text: str) -> List[str]:
        skills_section = self.find_section(text, "skills")
        search_text = skills_section if skills_section else text
        found = []
        for skill in self.skill_keywords:
            pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern, search_text, flags=re.IGNORECASE):
                found.append(skill.title())

        return self.depulicate(found)

    def extract_educations(self, text: str) -> List[str]:
        education_section = self.find_section(text, "education")
        if not education_section:
            return []
        lines = []
        for line in education_section.splitlines():
            stripped = line.strip("•- ").strip()
            if stripped:
                lines.append(stripped)
        return self.depulicate(lines)

    def extract_experience(self, text: str) -> List[Experience_Item]:
        experience_section = self.find_section(text, "experience")
        if not experience_section:
            return []

        blocks = self.split_blocks(experience_section)
        result: List[Experience_Item] = []

        for block in blocks:
            lines = []
            for line in block.splitlines():
                stripped = line.strip("•- ").strip()
                if stripped:
                    lines.append(stripped)

            if not lines:
                continue

            title = lines[0]
            company = lines[1] if len(lines) > 1 else None

            duration_text = None
            for line in lines[:4]:
                if re.search(r"(20\d{2}|19\d{2}|present|current)", line, flags=re.IGNORECASE):
                    duration_text = line
                    break

            description_lines = [line for line in lines[2:] if line != duration_text]
            description = " ".join(description_lines).strip() if description_lines else None

            result.append(
                Experience_Item(
                    title=title,
                    company=company,
                    duration_text=duration_text,
                    description_text=description,
                )
            )

        return result

    def extract_project_experience(self,text:str)->List[Project_Item]:
        project_section = self.find_section(text,"projects")
        if not project_section:
            return []
        blocks = self.split_blocks(project_section)
        result:List[Project_Item]=[]
        for block in blocks:
            lines = []
            for line in block.splitlines():
                    stripped = line.strip("•- ").strip()
                    if stripped:
                        lines.append(stripped)
            if not lines:
                continue

            project_name = lines[0]
            description_text = " ".join(lines[1:]) if len(lines)>1 else None

            technologies = []

            if description_text:
                for skill in self.skill_keywords:
                    pattern = rf"\b{re.escape(skill)}\b"
                    if re.search(pattern,description_text,re.IGNORECASE):
                        technologies.append(skill)


            result.append(
                Project_Item(
                    name=project_name,
                    description=description_text,
                    technologies=technologies

                )
            )

            return result




    def find_section(self, text: str, section_name: str) -> str | None:
        lines = text.splitlines()
        target_aliases = {alias.lower() for alias in self.section_aliases.get(section_name, [])}
        all_aliases = set()
        for alias_list in self.section_aliases.values():
            for alias in alias_list:
                all_aliases.add(alias.lower())

        start_index = None
        for i, line in enumerate(lines):
            cleaned_line = line.strip().lower()
            if cleaned_line in target_aliases:
                start_index = i
                break

        if start_index is None:
            return None

        collected = []
        for line in lines[start_index + 1 :]:
            cleaned_line = line.strip().lower()
            if cleaned_line in all_aliases:
                break
            if line.strip():
                collected.append(line.strip())

        if not collected:
            return None

        return "\n".join(collected)


    def split_blocks(self, text: str) -> List[str]:
        blocks = re.split(r"\n\s*\n", text)
        return [block.strip() for block in blocks if block.strip()]

    def depulicate(self, items: List[str]) -> List[str]:
        seen = set()
        result = []

        for item in items:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                result.append(item)

        return result
