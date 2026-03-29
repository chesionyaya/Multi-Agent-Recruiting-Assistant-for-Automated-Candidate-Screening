from pydantic import BaseModel
from typing import List

class Experience_Item(BaseModel):
    title:str
    company:str | None = None
    duration_text : str
    description_text:str | None = None

class Project_Item(BaseModel):
    name:str
    description:str | None=None
    technologies:List[str]=[]

class Candidate_Profile(BaseModel):
    name:str |None = None
    skills:List[str] = []
    education:List[str] = []
    experience:List[Experience_Item] = []
    raw_text:str


