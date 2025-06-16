from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models import Candidate, Job, MatchResult

# Load the model once at import time
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> np.ndarray:
    """
    Compute a dense embedding for `text` using a local SentenceTransformer model.
    """
    # returns a 1D numpy array
    return MODEL.encode(text, normalize_embeddings=True)

def ai_score(candidate: Candidate, job: Job) -> float:
    """
    Combine cosine similarity of embeddings with an experience factor.
    """
    # build the two texts
    cand_text = " ".join(candidate.skills) + " " + candidate.resumeText
    job_text = job.title + " " + job.description + " " + " ".join(job.requiredSkills)

    # embed both
    v1 = embed_text(cand_text)
    v2 = embed_text(job_text)

    # cosine similarity in [0,1]
    score = float(cosine_similarity([v1], [v2])[0][0])

    # experience factor: full if meets min, half otherwise
    exp_factor = 1.0 if candidate.experienceYears >= job.minExperience else 0.5

    # combine (80% semantic match, 20% experience)
    return round(score * 0.8 + exp_factor * 0.2, 4)

def match_candidate_to_jobs(candidate: Candidate, jobs: List[Job]) -> List[MatchResult]:
    """
    Score each job for the given candidate, then sort descending.
    """
    results: List[MatchResult] = []
    for job in jobs:
        score = ai_score(candidate, job)
        results.append(MatchResult(jobId=job.id, jobTitle=job.title, matchScore=score))
    # sort by matchScore desc
    return sorted(results, key=lambda x: x.matchScore, reverse=True)
