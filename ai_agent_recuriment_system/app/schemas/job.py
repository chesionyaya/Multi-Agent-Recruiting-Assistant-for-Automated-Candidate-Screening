from typing import List, Dict

from pydantic import BaseModel

class JobProfile(BaseModel):
    title:str
    must_have_skills:List[str]
    nice_to_have_skills:List[str]
    min_years_experience:float | None = None
    education_requirements:List[str]=[]
    weights:Dict[str,float]



