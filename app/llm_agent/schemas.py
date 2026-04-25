from pydantic import BaseModel, Field

from app.schemas.candidate import Experience_Item, Project_Item


class JDLLMOutput(BaseModel):
    title: str = "Unknown Role"
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    min_years_experience: float | None = None
    education_requirements: list[str] = Field(default_factory=list)


class CVLLMOutput(BaseModel):
    name: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience: list[Experience_Item] = Field(default_factory=list)
    project_experience: list[Project_Item] = Field(default_factory=list)

