import json

from app.agents.explanation_agent import Explanation_Agent
from app.llm_agent.clients.base import LLMClient
from app.llm_agent.clients.mock_client import MockLLMClient
from app.llm_agent.prompts.loader import PromptLoader
from app.llm_agent.tools.rag.base import Retriever
from app.schemas.candidate import Candidate_Profile
from app.schemas.job import JobProfile
from app.schemas.match_result import Match_Result


class ExplanationLLMAgent:
    def __init__(
        self,
        client: LLMClient | None = None,
        prompt_loader: PromptLoader | None = None,
        fallback_agent: Explanation_Agent | None = None,
        retriever: Retriever | None = None,
    ):
        self.client = client or MockLLMClient()
        self.prompt_loader = prompt_loader or PromptLoader()
        self.fallback_agent = fallback_agent or Explanation_Agent()
        self.retriever = retriever

    def run(
        self,
        candidate_profile: Candidate_Profile,
        job_profile: JobProfile,
        match_result: Match_Result | None = None,
    ) -> str:
        fallback_text = self.fallback_agent.run(candidate_profile, job_profile, match_result)

        try:
            system_prompt = self.prompt_loader.load("explanation")
            rag_context = self._retrieve_context(
                f"{job_profile.title} {' '.join(job_profile.must_have_skills)}"
            )
            user_payload = {
                "job_profile": job_profile.model_dump(),
                "candidate_profile": candidate_profile.model_dump(),
                "match_result": (match_result.model_dump() if match_result else {}),
                "rag_context": rag_context,
            }
            text = self.client.generate_text(
                system_prompt=system_prompt,
                user_prompt=json.dumps(user_payload, ensure_ascii=False),
            )
            clean = text.strip()
            return clean if clean else fallback_text
        except Exception:
            return fallback_text

    def _retrieve_context(self, query: str) -> list[str]:
        if self.retriever is None:
            return []
        return self.retriever.retrieve(query=query, top_k=5)

