from app.agents.cv_parsing_agent import CV_parsing_agent
from app.agents.explanation_agent import Explanation_Agent
from app.agents.jd_understanding_agent import Jd_understanding_agent
from app.agents.matching_agent import Matching_Agent
from app.agents.shortlist_agent import Shortlist_Agent
from app.llm_agent.agents.cv_llm_agent import CVLLMAgent
from app.llm_agent.agents.explanation_llm_agent import ExplanationLLMAgent
from app.llm_agent.agents.jd_llm_agent import JDLLMAgent
from app.llm_agent.router.strategy_router import StrategyRouter
from app.llm_agent.types import EngineMode, RouteDecision
from app.orchestration.pipeline import ScreenPipeline
from app.schemas.candidate import Candidate_Profile
from app.schemas.job import JobProfile
from app.schemas.match_result import Match_Result


class HybridScreenPipeline:
    def __init__(
        self,
        rule_pipeline: ScreenPipeline | None = None,
        router: StrategyRouter | None = None,
        jd_llm_agent: JDLLMAgent | None = None,
        cv_llm_agent: CVLLMAgent | None = None,
        explanation_llm_agent: ExplanationLLMAgent | None = None,
        matching_agent: Matching_Agent | None = None,
        shortlist_agent: Shortlist_Agent | None = None,
    ):
        self.rule_pipeline = rule_pipeline or ScreenPipeline(
            jd_agent=Jd_understanding_agent(),
            cv_agent=CV_parsing_agent(),
            matching_agent=Matching_Agent(),
            explanation_agent=Explanation_Agent(),
            shortlist_agent=Shortlist_Agent(),
        )
        self.router = router or StrategyRouter()
        self.jd_llm_agent = jd_llm_agent or JDLLMAgent()
        self.cv_llm_agent = cv_llm_agent or CVLLMAgent()
        self.explanation_llm_agent = explanation_llm_agent or ExplanationLLMAgent()
        self.matching_agent = matching_agent or Matching_Agent()
        self.shortlist_agent = shortlist_agent or Shortlist_Agent()

    def match_results(
        self,
        jd_text: str,
        cv_text: list[str],
        top_k: int | None = None,
        mode: EngineMode = "auto",
        include_route_meta: bool = False,
    ):
        route = self.router.route(jd_text=jd_text, cv_texts=cv_text, requested_mode=mode)

        if route.mode == "rule":
            results = self.rule_pipeline.match_results(jd_text=jd_text, cv_text=cv_text, top_k=top_k)
        elif route.mode == "llm":
            results = self._run_llm_pipeline(jd_text=jd_text, cv_text=cv_text, top_k=top_k)
        else:
            results = self._run_hybrid_pipeline(jd_text=jd_text, cv_text=cv_text, top_k=top_k)

        if include_route_meta:
            return results, route
        return results

    def _run_llm_pipeline(
        self,
        jd_text: str,
        cv_text: list[str],
        top_k: int | None = None,
    ) -> list[Match_Result]:
        job_profile = self.jd_llm_agent.run(jd_text)
        results = []
        for cv in cv_text:
            candidate_profile = self.cv_llm_agent.run(cv)
            match_result = self.matching_agent.run(job_profile, candidate_profile)
            match_result.explanation = self.explanation_llm_agent.run(
                candidate_profile=candidate_profile,
                job_profile=job_profile,
                match_result=match_result,
            )
            match_result.decision = self.shortlist_agent.run(match_result)
            results.append(match_result)

        ranked = sorted(results, key=lambda x: x.final_score, reverse=True)
        if top_k is not None:
            return ranked[:top_k]
        return ranked

    def _run_hybrid_pipeline(
        self,
        jd_text: str,
        cv_text: list[str],
        top_k: int | None = None,
    ) -> list[Match_Result]:
        rule_jd_profile = self.rule_pipeline._run_agent(self.rule_pipeline.jd_agent, jd_text)
        llm_jd_profile = self.jd_llm_agent.run(jd_text)
        merged_job = self._merge_job_profiles(rule_jd_profile, llm_jd_profile)

        results = []
        for cv in cv_text:
            rule_cv_profile = self.rule_pipeline._run_agent(self.rule_pipeline.cv_agent, cv)
            llm_cv_profile = self.cv_llm_agent.run(cv)
            merged_candidate = self._merge_candidate_profiles(rule_cv_profile, llm_cv_profile)

            match_result = self.matching_agent.run(merged_job, merged_candidate)
            match_result.explanation = self.explanation_llm_agent.run(
                candidate_profile=merged_candidate,
                job_profile=merged_job,
                match_result=match_result,
            )
            match_result.decision = self.shortlist_agent.run(match_result)
            results.append(match_result)

        ranked = sorted(results, key=lambda x: x.final_score, reverse=True)
        if top_k is not None:
            return ranked[:top_k]
        return ranked

    def route(
        self,
        jd_text: str,
        cv_text: list[str],
        requested_mode: EngineMode = "auto",
    ) -> RouteDecision:
        return self.router.route(jd_text=jd_text, cv_texts=cv_text, requested_mode=requested_mode)

    def _merge_job_profiles(self, rule_profile: JobProfile, llm_profile: JobProfile) -> JobProfile:
        return JobProfile(
            title=self._pick_title(rule_profile.title, llm_profile.title),
            must_have_skills=self._union(rule_profile.must_have_skills, llm_profile.must_have_skills),
            nice_to_have_skills=self._union(rule_profile.nice_to_have_skills, llm_profile.nice_to_have_skills),
            min_years_experience=(
                llm_profile.min_years_experience
                if llm_profile.min_years_experience is not None
                else rule_profile.min_years_experience
            ),
            education_requirements=self._union(
                rule_profile.education_requirements, llm_profile.education_requirements
            ),
            weights=rule_profile.weights,
        )

    def _merge_candidate_profiles(
        self,
        rule_profile: Candidate_Profile,
        llm_profile: Candidate_Profile,
    ) -> Candidate_Profile:
        return Candidate_Profile(
            name=llm_profile.name or rule_profile.name,
            skills=self._union(rule_profile.skills, llm_profile.skills),
            education=self._union(rule_profile.education, llm_profile.education),
            experience=llm_profile.experience or rule_profile.experience,
            project_experience=self._merge_projects(
                rule_profile.project_experience, llm_profile.project_experience
            ),
            raw_text=rule_profile.raw_text,
        )

    def _merge_projects(self, first, second):
        merged = list(first)
        known_names = {project.name.lower().strip() for project in merged}
        for project in second:
            key = project.name.lower().strip()
            if key not in known_names:
                known_names.add(key)
                merged.append(project)
        return merged

    def _pick_title(self, rule_title: str, llm_title: str) -> str:
        if llm_title and llm_title.lower() != "unknown role":
            return llm_title
        return rule_title

    def _union(self, first: list[str], second: list[str]) -> list[str]:
        seen = set()
        result = []
        for item in first + second:
            key = item.lower().strip()
            if key and key not in seen:
                seen.add(key)
                result.append(item.strip())
        return result

