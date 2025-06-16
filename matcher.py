from typing import List
from models import Candidate, Job, MatchResult

def calculate_score(candidate: Candidate, job: Job) -> float:
    skill_overlap = len(set(candidate.skills) & set(job.requiredSkills))
    total_required = len(set(job.requiredSkills))
    skill_score = skill_overlap / total_required if total_required else 0

    exp_score = 1.0 if candidate.experienceYears >= job.minExperience else 0.5

    return round((skill_score * 0.7 + exp_score * 0.3) * 100, 2)

def match_candidate_to_jobs(candidate: Candidate, jobs: List[Job]) -> List[MatchResult]:
    results = []
    for job in jobs:
        score = calculate_score(candidate, job)
        results.append(MatchResult(jobId=job.id, jobTitle=job.title, matchScore=score))
    return sorted(results, key=lambda x: x.matchScore, reverse=True)
