from pydantic import BaseModel
from typing import List, Dict


class MatchResult(BaseModel):
    candidate_name: str | None = None
    skill_score: float
    experience_score: float
    project_score: float
    education_score: float
    final_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    decision: str
    explanation: str
    score_breakdown: Dict[str, float] = {}