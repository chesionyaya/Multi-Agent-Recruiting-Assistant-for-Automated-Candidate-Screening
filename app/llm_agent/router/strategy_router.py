import re

from app.llm_agent.types import EngineMode, RouteDecision


class StrategyRouter:
    SECTION_HINTS = {"skills", "experience", "education", "projects", "required", "preferred"}

    def route(self, jd_text: str, cv_texts: list[str], requested_mode: EngineMode = "auto") -> RouteDecision:
        if requested_mode in {"rule", "llm", "hybrid"}:
            return RouteDecision(
                mode=requested_mode,
                reason=f"Mode forced by caller: {requested_mode}",
                confidence=1.0,
            )

        combined_text = " ".join([jd_text, *cv_texts]).strip()
        non_ascii_ratio = self._non_ascii_ratio(combined_text)
        format_score = self._format_score(jd_text, cv_texts)
        avg_len = self._average_length(cv_texts)

        if non_ascii_ratio > 0.25:
            return RouteDecision(
                mode="llm",
                reason="Detected highly mixed language content; LLM extraction preferred.",
                confidence=0.82,
            )

        if format_score >= 0.6 and avg_len <= 3500:
            return RouteDecision(
                mode="rule",
                reason="Structured CV/JD format detected; rule-based parser is reliable.",
                confidence=0.74,
            )

        if avg_len > 3500:
            return RouteDecision(
                mode="hybrid",
                reason="Long or dense CV text detected; using hybrid parsing for robustness.",
                confidence=0.78,
            )

        return RouteDecision(
            mode="llm",
            reason="Unclear formatting; LLM parsing is likely more robust.",
            confidence=0.68,
        )

    def _average_length(self, cv_texts: list[str]) -> int:
        if not cv_texts:
            return 0
        return int(sum(len(item) for item in cv_texts) / len(cv_texts))

    def _format_score(self, jd_text: str, cv_texts: list[str]) -> float:
        text = f"{jd_text}\n" + "\n".join(cv_texts)
        low = text.lower()
        hit = sum(1 for hint in self.SECTION_HINTS if hint in low)
        return min(1.0, hit / max(1, len(self.SECTION_HINTS)))

    def _non_ascii_ratio(self, text: str) -> float:
        if not text:
            return 0.0
        non_ascii = len(re.findall(r"[^\x00-\x7F]", text))
        return non_ascii / len(text)

