from dataclasses import dataclass
from typing import Literal


EngineMode = Literal["auto", "rule", "llm", "hybrid"]
ResolvedMode = Literal["rule", "llm", "hybrid"]


@dataclass
class RouteDecision:
    mode: ResolvedMode
    reason: str
    confidence: float

