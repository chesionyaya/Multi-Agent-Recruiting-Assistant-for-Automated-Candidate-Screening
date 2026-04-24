import re
from datetime import datetime

from app.schemas.candidate import Candidate_Profile
from app.schemas.job import JobProfile
from app.schemas.match_result import Match_Result


class Matching_Agent:
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

    def run(self, job_profile: JobProfile, candidate_profile: Candidate_Profile) -> Match_Result:
        skill_score, matched_skills, missing_skills = self.score_skills(job_profile, candidate_profile)
        education_score = self.score_education(job_profile, candidate_profile)
        experience_score = self.score_experience(job_profile, candidate_profile)
        project_score = self.score_project(job_profile, candidate_profile)
        bonus_score = self.score_bonus(job_profile, candidate_profile)

        weights = job_profile.weights
        final_score = (
            skill_score * weights.get("skills", 0.0)
            + experience_score * weights.get("experience", 0.0)
            + project_score * weights.get("projects", 0.0)
            + education_score * weights.get("education", 0.0)
            + bonus_score * weights.get("bonus", 0.0)
        )
        final_score = max(0.0, min(1.0, final_score))

        strengths, risks = self.build_strengths_and_risks(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            education_score=education_score,
            experience_score=experience_score,
            project_score=project_score,
            bonus_score=bonus_score,
        )

        return Match_Result(
            candidate_name=candidate_profile.name,
            final_score=round(final_score, 4),
            skill_score=round(skill_score, 4),
            education_score=round(education_score, 4),
            experience_score=round(experience_score, 4),
            project_score=round(project_score, 4),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            strengths=strengths,
            risks=risks,
        )

    def score_skills(self, job_profile: JobProfile, candidate_profile: Candidate_Profile):
        candidate_skills = {s.lower().strip() for s in candidate_profile.skills}
        must_have = [s.lower().strip() for s in job_profile.must_have_skills]
        nice_to_have = [s.lower().strip() for s in job_profile.nice_to_have_skills]

        matched_must = [s.title() for s in must_have if s in candidate_skills]
        missing_must = [s.title() for s in must_have if s not in candidate_skills]
        matched_nice = [s.title() for s in nice_to_have if s in candidate_skills]

        must_ratio = len(matched_must) / len(must_have) if must_have else 1.0
        nice_ratio = len(matched_nice) / len(nice_to_have) if nice_to_have else 0.0
        if must_have or nice_to_have:
            score = (must_ratio * 0.8) + (nice_ratio * 0.2)
        else:
            score = 0.0

        return (
            max(0.0, min(1.0, score)),
            self.deduplicate(matched_must + matched_nice),
            self.deduplicate(missing_must),
        )

    def score_education(self, job_profile: JobProfile, candidate_profile: Candidate_Profile) -> float:
        requirements = [r.lower().strip() for r in job_profile.education_requirements]
        if not requirements:
            return 1.0

        profile_text = " ".join(candidate_profile.education).lower()
        matched = sum(1 for req in requirements if req in profile_text)
        return max(0.0, min(1.0, matched / len(requirements)))

    def score_experience(self, job_profile: JobProfile, candidate_profile: Candidate_Profile) -> float:
        min_years = job_profile.min_years_experience
        if min_years is None:
            return 1.0

        required_years = float(min_years)
        if required_years <= 0:
            return 1.0

        total_years = 0.0
        for exp in candidate_profile.experience:
            total_years += self.estimate_years(exp.duration_text)

        return max(0.0, min(1.0, total_years / required_years))

    def score_project(self, job_profile: JobProfile, candidate_profile: Candidate_Profile) -> float:
        projects = candidate_profile.project_experience
        if not projects:
            return 0.0

        role_skills = {
            s.lower().strip()
            for s in (job_profile.must_have_skills + job_profile.nice_to_have_skills)
        }
        if not role_skills:
            return min(1.0, len(projects) / 2.0)

        project_text = " ".join(
            f"{p.name or ''} {p.description or ''} {' '.join(p.technologies)}".lower()
            for p in projects
        )
        matched = sum(1 for skill in role_skills if skill in project_text)
        return max(0.0, min(1.0, matched / len(role_skills)))

    def score_bonus(self, job_profile: JobProfile, candidate_profile: Candidate_Profile) -> float:
        required = {s.lower().strip() for s in job_profile.must_have_skills}
        preferred = {s.lower().strip() for s in job_profile.nice_to_have_skills}
        candidate = {s.lower().strip() for s in candidate_profile.skills}

        extra = candidate - required - preferred
        if not extra:
            return 0.0
        return min(1.0, len(extra) / 10.0)

    def build_strengths_and_risks(
        self,
        matched_skills,
        missing_skills,
        education_score,
        experience_score,
        project_score,
        bonus_score,
    ):
        strengths = []
        risks = []

        if matched_skills:
            strengths.append(f"Matched skills: {', '.join(matched_skills)}")
        if education_score >= 0.7:
            strengths.append("Education background aligns well with requirements.")
        if experience_score >= 0.7:
            strengths.append("Experience meets or exceeds the role expectation.")
        if project_score >= 0.5:
            strengths.append("Project experience appears relevant to this role.")
        if bonus_score > 0:
            strengths.append("Has additional skills beyond the core role requirements.")

        if missing_skills:
            risks.append(f"Missing required skills: {', '.join(missing_skills)}")
        if education_score < 0.5:
            risks.append("Education alignment is limited.")
        if experience_score < 0.5:
            risks.append("Experience may be below the minimum requirement.")
        if project_score < 0.3:
            risks.append("Limited project evidence for role-specific skills.")

        return strengths, risks

    def estimate_years(self, duration_text: str | None) -> float:
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

        years = [int(y) for y in re.findall(r"(19\d{2}|20\d{2})", text)]
        current_year = datetime.now().year

        if len(years) >= 2:
            start, end = years[0], years[1]
            return max(0.0, float(end - start))
        if len(years) == 1 and ("present" in text or "current" in text):
            return max(0.0, float(current_year - years[0]))

        months = re.findall(r"(\d+)\s+months?", text)
        if months:
            return max(0.0, int(months[0]) / 12.0)

        return 0.0

    def deduplicate(self, items):
        seen = set()
        result = []
        for item in items:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result
