from dataclasses import dataclass


@dataclass
class LLMSettings:
    model_name: str = "gpt-4.1-mini"
    temperature: float = 0.0
    max_tokens: int = 1200
    timeout_seconds: int = 30

