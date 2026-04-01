from pydantic import BaseModel,Field
from typing import List
class Match_Result(BaseModel):
    candidate_name: str | None = None

    final_score: float = 0.0
    skill_score: float = 0.0
    education_score: float = 0.0
    experience_score: float = 0.0
    project_score: float = 0.0

    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)

    strengths: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)

    explanation: str | None = None
    decision: str | None = None
