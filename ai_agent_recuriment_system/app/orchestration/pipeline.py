from typing import List
class ScreenPipeline:
    def __init__(self,jd_agent,cv_agent,matching_agent,explanation_agent,shortlist_agent):
        self.jd_agent = jd_agent
        self.cv_agent = cv_agent
        self.matching_agent = matching_agent
        self.explanation_agent = explanation_agent
        self.shortlist_agent = shortlist_agent

    def match_results(self,jd_text:str,cv_text:List[str]):
        job_profile = self.jd_agent(jd_text)
        results = []
        for cv in cv_text:
           candidate_profile =  self.cv_agent.run(cv)
           match_result = self.matching_agent.run(job_profile,candidate_profile)
           match_result.explanation = self.explanation_agent.run(candidate_profile,job_profile)
           match_result.decision = self.shortlist_agent.run(match_result)
           results.append(match_result)

        return sorted(results,key=lambda x:x.final_score,reverse=True)



