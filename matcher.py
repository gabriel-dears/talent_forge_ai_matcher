from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models import Candidate, Job, MatchResult

# Load the embedding model once at import time to avoid repeated initialization
MODEL: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> np.ndarray:
    """
    Convert input text into a normalized dense vector using SentenceTransformer.

    Args:
        text (str): A string to embed, typically a job or candidate profile.

    Returns:
        np.ndarray: A 1D NumPy array representing the embedded text vector.
    """
    return MODEL.encode(text, normalize_embeddings=True)


def ai_score(candidate: Candidate, job: Job) -> float:
    """
    Calculate a match score between a candidate and a job based on semantic similarity
    and experience alignment.

    Args:
        candidate (Candidate): The candidate to evaluate.
        job (Job): The job to compare against.

    Returns:
        float: A score between 0 and 1 indicating the quality of the match.
    """
    # Concatenate candidate profile into a unified text
    cand_text: str = " ".join(candidate.skills) + " " + candidate.resumeText

    # Concatenate job description into a unified text
    job_text: str = job.title + " " + job.description + " " + " ".join(job.requiredSkills)

    # Embed both candidate and job texts
    candidate_vector: np.ndarray = embed_text(cand_text)
    job_vector: np.ndarray = embed_text(job_text)

    # Compute cosine similarity between embeddings
    similarity_score: float = float(cosine_similarity([candidate_vector], [job_vector])[0][0])

    # Add experience factor (1.0 if candidate meets or exceeds requirement, else 0.5)
    experience_factor: float = 1.0 if candidate.experienceYears >= job.minExperience else 0.5

    # Final score is 80% semantic match + 20% experience alignment
    final_score: float = round(similarity_score * 0.8 + experience_factor * 0.2, 4)
    return final_score


def match_candidate_to_jobs(candidate: Candidate, jobs: List[Job]) -> List[MatchResult]:
    """
    Evaluate and rank a list of jobs based on how well they match the given candidate.

    Args:
        candidate (Candidate): The candidate to match.
        jobs (List[Job]): A list of available jobs to evaluate.

    Returns:
        List[MatchResult]: A list of match results sorted by score (descending).
    """
    match_results: List[MatchResult] = [
        MatchResult(
            jobId=job.id,
            jobTitle=job.title,
            matchScore=ai_score(candidate, job)
        )
        for job in jobs
    ]

    return sorted(match_results, key=lambda result: result.matchScore, reverse=True)
