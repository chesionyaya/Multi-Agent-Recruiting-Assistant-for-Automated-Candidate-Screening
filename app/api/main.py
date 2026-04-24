from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse

from app.agents.cv_parsing_agent import CV_parsing_agent
from app.agents.explanation_agent import Explanation_Agent
from app.agents.jd_understanding_agent import Jd_understanding_agent
from app.agents.matching_agent import Matching_Agent
from app.agents.shortlist_agent import Shortlist_Agent
from app.orchestration.pipeline import ScreenPipeline

app = FastAPI()
API_DIR = Path(__file__).resolve().parent

pipeline = ScreenPipeline(
    jd_agent=Jd_understanding_agent(),
    cv_agent=CV_parsing_agent(),
    matching_agent=Matching_Agent(),
    explanation_agent=Explanation_Agent(),
    shortlist_agent=Shortlist_Agent()
)

class RequestScreen(BaseModel):
    cv_text: list[str]
    jd_text: str
    top_k: int | None = None


@app.get("/")
def home():
    return FileResponse(API_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/screen")
def screen(req: RequestScreen):
    result = pipeline.match_results(jd_text=req.jd_text, cv_text=req.cv_text, top_k=req.top_k)
    return [r.model_dump() for r in result]
