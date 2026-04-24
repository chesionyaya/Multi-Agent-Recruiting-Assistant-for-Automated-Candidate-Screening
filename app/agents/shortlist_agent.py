from app.schemas.match_result import Match_Result


class Shortlist_Agent:
    def __init__(
        self,
        shortlist_threshold: float = 0.75,
        review_threshold: float = 0.55,
        max_missing_for_shortlist: int = 1,
    ):
        self.shortlist_threshold = shortlist_threshold
        self.review_threshold = review_threshold
        self.max_missing_for_shortlist = max_missing_for_shortlist

    def run(self, match_result: Match_Result) -> str:
        score = match_result.final_score
        missing_count = len(match_result.missing_skills)
        has_experience_risk = match_result.experience_score < 0.5
        has_skill_risk = missing_count > 0

        if (
            score >= self.shortlist_threshold
            and missing_count <= self.max_missing_for_shortlist
            and not has_experience_risk
        ):
            return "Shortlist"

        if score < self.review_threshold:
            return "Reject"

        if missing_count >= 3:
            return "Reject"

        if has_skill_risk or has_experience_risk:
            return "Review"

        return "Shortlist"
