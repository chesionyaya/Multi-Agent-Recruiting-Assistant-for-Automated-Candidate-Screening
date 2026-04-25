import json

from pydantic import BaseModel

from app.llm_agent.clients.base import LLMClient, TModel
from app.llm_agent.config import LLMSettings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None


class OpenAILLMClient(LLMClient):
    """
    Thin wrapper around OpenAI chat completion.
    This class is optional and only used when `openai` package is installed.
    """

    def __init__(self, api_key: str, settings: LLMSettings | None = None):
        if OpenAI is None:
            raise ImportError("openai package not installed. Run `pip install openai`.")
        self.settings = settings or LLMSettings()
        self.client = OpenAI(api_key=api_key)

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[TModel],
    ) -> TModel:
        response = self.client.chat.completions.create(
            model=self.settings.model_name,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = response.choices[0].message.content or "{}"
        payload = self._extract_json(text)
        return response_model.model_validate(payload)

    def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.model_name,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""

    def _extract_json(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json", "", 1).strip()
        return json.loads(text)

