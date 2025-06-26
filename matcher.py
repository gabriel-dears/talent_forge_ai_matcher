from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

from models import Candidate, Job, MatchResult
from redis_client import redis_client

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
MATCH_THRESHOLD = 0.5  # Filter out poor matches


def embed_text(text: str) -> np.ndarray:
    return MODEL.encode(text, normalize_embeddings=True)


def cache_or_compute_embedding(key: str, text: str) -> np.ndarray:
    cached = redis_client.get(key)
    if cached:
        return pickle.loads(cached)
    vec = embed_text(text)
    redis_client.set(key, pickle.dumps(vec))
    return vec


def compute_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return float(np.dot(vec1, vec2.T))


def ai_score(candidate: Candidate, job: Job) -> float:
    """
    Score a candidate-job match using semantic similarity + experience.
    """
    # Embedding keys
    job_key = f"embedding:job:{job.id}"
    cand_resume_key = f"embedding:candidate:resume:{candidate.id}"
    cand_skills_key = f"embedding:candidate:skills:{candidate.id}"

    # Text sources
    job_text = f"{job.title} {job.description} {' '.join(job.requiredSkills)}"
    cand_resume_text = candidate.resumeText
    cand_skills_text = " ".join(candidate.skills)

    # Get or compute embeddings
    job_vec = cache_or_compute_embedding(job_key, job_text)
    resume_vec = cache_or_compute_embedding(cand_resume_key, cand_resume_text)
    skills_vec = cache_or_compute_embedding(cand_skills_key, cand_skills_text)

    # Weighted semantic similarity
    sem_score = (
        compute_similarity(skills_vec, job_vec) * 0.6 +
        compute_similarity(resume_vec, job_vec) * 0.4
    )

    # Experience scaling
    experience_ratio = min(candidate.experienceYears / max(1, job.minExperience), 2.0)
    experience_factor = min(1.0, experience_ratio)

    # Final weighted score
    final_score = round(sem_score * 0.8 + experience_factor * 0.2, 4)
    return final_score


def match_candidate_to_jobs(candidate: Candidate, jobs: List[Job]) -> List[MatchResult]:
    results = []
    for job in jobs:
        score = ai_score(candidate, job)
        if score >= MATCH_THRESHOLD:
            results.append(MatchResult(
                jobId=job.id,
                jobTitle=job.title,
                matchScore=score
            ))

    return sorted(results, key=lambda x: x.matchScore, reverse=True)
