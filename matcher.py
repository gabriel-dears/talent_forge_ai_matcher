import os
import numpy as np
import openai
from typing import List
from models import Candidate, Job, MatchResult
from sklearn.metrics.pairwise import cosine_similarity

# configure your OpenAI key via env var OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

def embed_text(text: str) -> np.ndarray:
    resp = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(resp["data"][0]["embedding"])

def ai_score(candidate: Candidate, job: Job) -> float:
    # build the two texts
    cand_text = " ".join(candidate.skills) + " " + candidate.resumeText
    job_text = job.title + " " + job.description + " " + " ".join(job.requiredSkills)
    # embed
    v1, v2 = embed_text(cand_text), embed_text(job_text)
    # cosine similarity
    score = cosine_similarity([v1], [v2])[0][0]
    # combine with experience penalty/bonus
    exp_factor = 1.0 if candidate.experienceYears >= job.minExperience else 0.5
    return round(float(score * 0.8 + exp_factor * 0.2), 4)

def match_candidate_to_jobs(candidate: Candidate, jobs: List[Job]) -> List[MatchResult]:
    results = []
    for job in jobs:
        score = ai_score(candidate, job)
        results.append(MatchResult(jobId=job.id, jobTitle=job.title, matchScore=score))
    return sorted(results, key=lambda x: x.matchScore, reverse=True)
