from typing import List


class ScreenPipeline:
    def __init__(self, jd_agent, cv_agent, matching_agent, explanation_agent, shortlist_agent):
        self.jd_agent = jd_agent
        self.cv_agent = cv_agent
        self.matching_agent = matching_agent
        self.explanation_agent = explanation_agent
        self.shortlist_agent = shortlist_agent

    def match_results(self, jd_text: str, cv_text: List[str], top_k: int = None):
        job_profile = self._run_agent(self.jd_agent, jd_text)
        results = []
        for cv in cv_text:
            candidate_profile = self._run_agent(self.cv_agent, cv)
            match_result = self._run_agent(self.matching_agent, job_profile, candidate_profile)
            match_result.explanation = self._run_agent(
                self.explanation_agent, candidate_profile, job_profile, match_result
            )
            match_result.decision = self._run_agent(self.shortlist_agent, match_result)
            results.append(match_result)

        ranked_results = sorted(results, key=lambda x: x.final_score, reverse=True)

        if top_k is not None:
            return ranked_results[:top_k]

        return ranked_results

    @staticmethod
    def _run_agent(agent, *args):
        if hasattr(agent, "run") and callable(agent.run):
            return agent.run(*args)
        if callable(agent):
            return agent(*args)
        raise TypeError(f"Agent {agent} is not callable and has no run method.")

