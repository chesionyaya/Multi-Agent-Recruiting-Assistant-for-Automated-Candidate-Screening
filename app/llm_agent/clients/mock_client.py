from app.llm_agent.clients.base import LLMClient, TModel


class MockLLMClient(LLMClient):
    """
    Local deterministic client for development.
    It intentionally raises for structured calls so agents use fallback parsers.
    """

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[TModel],
    ) -> TModel:
        raise RuntimeError("MockLLMClient does not provide structured output.")

    def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return "Mock explanation: fallback mode used."

