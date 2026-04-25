from app.agents.cv_parsing_agent import CV_parsing_agent
from app.llm_agent.clients.base import LLMClient
from app.llm_agent.clients.mock_client import MockLLMClient
from app.llm_agent.prompts.loader import PromptLoader
from app.llm_agent.schemas import CVLLMOutput
from app.schemas.candidate import Candidate_Profile


class CVLLMAgent:
    def __init__(
        self,
        client: LLMClient | None = None,
        prompt_loader: PromptLoader | None = None,
        fallback_agent: CV_parsing_agent | None = None,
    ):
        self.client = client or MockLLMClient()
        self.prompt_loader = prompt_loader or PromptLoader()
        self.fallback_agent = fallback_agent or CV_parsing_agent()

    def run(self, cv_text: str) -> Candidate_Profile:
        try:
            system_prompt = self.prompt_loader.load("cv_extract")
            llm_result = self.client.generate_structured(
                system_prompt=system_prompt,
                user_prompt=cv_text,
                response_model=CVLLMOutput,
            )
            return Candidate_Profile(
                name=llm_result.name,
                skills=self._deduplicate(llm_result.skills),
                education=self._deduplicate(llm_result.education),
                experience=llm_result.experience,
                project_experience=llm_result.project_experience,
                raw_text=cv_text,
            )
        except Exception:
            return self.fallback_agent.run(cv_text)

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

