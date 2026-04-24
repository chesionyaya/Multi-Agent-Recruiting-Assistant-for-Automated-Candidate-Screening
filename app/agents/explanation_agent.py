import re
from datetime import datetime

from app.schemas.candidate import Candidate_Profile
from app.schemas.job import JobProfile
from app.schemas.match_result import Match_Result


class Explanation_Agent:
    MONTH_MAP = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    def run(
        self,
        candidate_profile: Candidate_Profile,
        job_profile: JobProfile,
        match_result: Match_Result | None = None,
    ) -> str:
        result = match_result or self._build_lightweight_match(job_profile, candidate_profile)
        name = candidate_profile.name or "This candidate"
        score_percent = round(result.final_score * 100)

        lines = [
            f"{name} has an overall match score of {score_percent}% for {job_profile.title}."
        ]

        if result.matched_skills:
            lines.append(f"Matched skills: {', '.join(result.matched_skills)}.")
        if result.missing_skills:
            lines.append(f"Missing required skills: {', '.join(result.missing_skills)}.")

        lines.append(
            "Score breakdown:"
            f" skills {round(result.skill_score * 100)}%,"
            f" experience {round(result.experience_score * 100)}%,"
            f" projects {round(result.project_score * 100)}%,"
            f" education {round(result.education_score * 100)}%."
        )

        if result.strengths:
            lines.append(f"Strengths: {'; '.join(result.strengths)}.")
        if result.risks:
            lines.append(f"Risks: {'; '.join(result.risks)}.")

        return " ".join(lines)

    def _build_lightweight_match(
        self, job_profile: JobProfile, candidate_profile: Candidate_Profile
    ) -> Match_Result:
        candidate_skills = {skill.lower().strip() for skill in candidate_profile.skills}
        must_have = [skill.lower().strip() for skill in job_profile.must_have_skills]
        nice_to_have = [skill.lower().strip() for skill in job_profile.nice_to_have_skills]

        matched_must = [skill.title() for skill in must_have if skill in candidate_skills]
        missing_must = [skill.title() for skill in must_have if skill not in candidate_skills]
        matched_nice = [skill.title() for skill in nice_to_have if skill in candidate_skills]

        must_ratio = len(matched_must) / len(must_have) if must_have else 1.0
        nice_ratio = len(matched_nice) / len(nice_to_have) if nice_to_have else 0.0
        skill_score = (must_ratio * 0.8 + nice_ratio * 0.2) if (must_have or nice_to_have) else 0.0

        education_score = self._score_education(job_profile, candidate_profile)
        experience_score = self._score_experience(job_profile, candidate_profile)
        project_score = self._score_project(job_profile, candidate_profile)
        bonus_score = self._score_bonus(job_profile, candidate_profile)

        weights = job_profile.weights
        final_score = (
            skill_score * weights.get("skills", 0.0)
            + experience_score * weights.get("experience", 0.0)
            + project_score * weights.get("projects", 0.0)
            + education_score * weights.get("education", 0.0)
            + bonus_score * weights.get("bonus", 0.0)
        )
        final_score = max(0.0, min(1.0, final_score))

        strengths = []
        risks = []

        if matched_must or matched_nice:
            strengths.append(
                f"Matched skills: {', '.join(self._deduplicate(matched_must + matched_nice))}"
            )
        if experience_score >= 0.7:
            strengths.append("Experience appears to meet the role expectation.")
        if education_score >= 0.7:
            strengths.append("Education background is aligned with requirements.")

        if missing_must:
            risks.append(f"Missing required skills: {', '.join(self._deduplicate(missing_must))}")
        if experience_score < 0.5:
            risks.append("Experience may be below the minimum requirement.")
        if project_score < 0.3:
            risks.append("Limited project evidence for role-specific skills.")

        return Match_Result(
            candidate_name=candidate_profile.name,
            final_score=round(final_score, 4),
            skill_score=round(skill_score, 4),
            education_score=round(education_score, 4),
            experience_score=round(experience_score, 4),
            project_score=round(project_score, 4),
            matched_skills=self._deduplicate(matched_must + matched_nice),
            missing_skills=self._deduplicate(missing_must),
            strengths=strengths,
            risks=risks,
        )

    def _score_education(self, job_profile: JobProfile, candidate_profile: Candidate_Profile) -> float:
        requirements = [req.lower().strip() for req in job_profile.education_requirements]
        if not requirements:
            return 1.0

        education_text = " ".join(candidate_profile.education).lower()
        matched = sum(1 for req in requirements if req in education_text)
        return max(0.0, min(1.0, matched / len(requirements)))

    def _score_experience(self, job_profile: JobProfile, candidate_profile: Candidate_Profile) -> float:
        if job_profile.min_years_experience is None:
            return 1.0

        required_years = float(job_profile.min_years_experience)
        if required_years <= 0:
            return 1.0

        total_years = sum(self._estimate_years(exp.duration_text) for exp in candidate_profile.experience)
        return max(0.0, min(1.0, total_years / required_years))

    def _score_project(self, job_profile: JobProfile, candidate_profile: Candidate_Profile) -> float:
        projects = candidate_profile.project_experience
        if not projects:
            return 0.0

        role_skills = {
            skill.lower().strip()
            for skill in (job_profile.must_have_skills + job_profile.nice_to_have_skills)
        }
        if not role_skills:
            return min(1.0, len(projects) / 2.0)

        project_text = " ".join(
            f"{project.name or ''} {project.description or ''} {' '.join(project.technologies)}".lower()
            for project in projects
        )
        matched = sum(1 for skill in role_skills if skill in project_text)
        return max(0.0, min(1.0, matched / len(role_skills)))

    def _score_bonus(self, job_profile: JobProfile, candidate_profile: Candidate_Profile) -> float:
        required = {skill.lower().strip() for skill in job_profile.must_have_skills}
        preferred = {skill.lower().strip() for skill in job_profile.nice_to_have_skills}
        candidate = {skill.lower().strip() for skill in candidate_profile.skills}

        extra = candidate - required - preferred
        if not extra:
            return 0.0
        return min(1.0, len(extra) / 10.0)

    def _estimate_years(self, duration_text: str | None) -> float:
        if not duration_text:
            return 0.0

        text = duration_text.lower()
        month_year_matches = re.findall(
            r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(19\d{2}|20\d{2})\b",
            text,
        )
        if len(month_year_matches) >= 2:
            (start_mon, start_year), (end_mon, end_year) = month_year_matches[0], month_year_matches[1]
            start_idx = int(start_year) * 12 + self.MONTH_MAP[start_mon[:3]]
            end_idx = int(end_year) * 12 + self.MONTH_MAP[end_mon[:3]]
            return max(0.0, (end_idx - start_idx) / 12.0)

        years = [int(year) for year in re.findall(r"(19\d{2}|20\d{2})", text)]
        current_year = datetime.now().year

        if len(years) >= 2:
            return max(0.0, float(years[1] - years[0]))
        if len(years) == 1 and ("present" in text or "current" in text):
            return max(0.0, float(current_year - years[0]))

        months = re.findall(r"(\d+)\s+months?", text)
        if months:
            return max(0.0, int(months[0]) / 12.0)

        return 0.0

    def _deduplicate(self, items):
        seen = set()
        result = []
        for item in items:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result
