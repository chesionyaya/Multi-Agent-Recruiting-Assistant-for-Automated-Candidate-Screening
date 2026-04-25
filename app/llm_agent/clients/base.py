from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


class LLMClient(ABC):
    @abstractmethod
    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[TModel],
    ) -> TModel:
        raise NotImplementedError

    @abstractmethod
    def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        raise NotImplementedError

