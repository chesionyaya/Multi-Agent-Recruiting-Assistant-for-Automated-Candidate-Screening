from app.agents.jd_understanding_agent import Jd_understanding_agent
from app.llm_agent.clients.base import LLMClient
from app.llm_agent.clients.mock_client import MockLLMClient
from app.llm_agent.prompts.loader import PromptLoader
from app.llm_agent.schemas import JDLLMOutput
from app.schemas.job import JobProfile


class JDLLMAgent:
    def __init__(
        self,
        client: LLMClient | None = None,
        prompt_loader: PromptLoader | None = None,
        fallback_agent: Jd_understanding_agent | None = None,
    ):
        self.client = client or MockLLMClient()
        self.prompt_loader = prompt_loader or PromptLoader()
        self.fallback_agent = fallback_agent or Jd_understanding_agent()

    def run(self, jd_text: str) -> JobProfile:
        try:
            system_prompt = self.prompt_loader.load("jd_extract")
            llm_result = self.client.generate_structured(
                system_prompt=system_prompt,
                user_prompt=jd_text,
                response_model=JDLLMOutput,
            )
            return JobProfile(
                title=llm_result.title,
                must_have_skills=self._deduplicate(llm_result.must_have_skills),
                nice_to_have_skills=self._deduplicate(llm_result.nice_to_have_skills),
                min_years_experience=llm_result.min_years_experience,
                education_requirements=self._deduplicate(llm_result.education_requirements),
                weights=self._default_weights(),
            )
        except Exception:
            return self.fallback_agent.run(job_texts=jd_text)

    @staticmethod
    def _default_weights() -> dict[str, float]:
        return {
            "skills": 0.4,
            "experience": 0.2,
            "projects": 0.2,
            "education": 0.1,
            "bonus": 0.1,
        }

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        seen = set()
        result = []
        for item in items:
            key = item.lower().strip()
            if key and key not in seen:
                seen.add(key)
                result.append(item.strip())
        return result

