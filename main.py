import os
from typing import List

from fastapi import FastAPI, HTTPException

from candidate_fetcher import fetch_candidate, fetch_candidates
from consumer import consume_candidates
from job_fetcher import fetch_jobs, fetch_job
from matcher import match_candidate_to_jobs, ai_score
from models import MatchResult

app = FastAPI()

# Base URL for the Spring Boot API (defaults to local if env not set)
SPRING_BASE: str = os.getenv("SPRING_API_URL", "http://localhost:8080/api/v1")


@app.get("/match/candidate/{candidate_id}", response_model=List[MatchResult])
async def match_for_candidate(candidate_id: str) -> List[MatchResult]:
    """
    Match a specific candidate against all available jobs.

    Args:
        candidate_id (str): The unique ID of the candidate to match.

    Returns:
        List[MatchResult]: A sorted list of jobs ranked by match score.

    Raises:
        HTTPException: If the candidate is not found or if job fetch fails.
    """
    # Fetch candidate data from external Spring Boot API
    candidate = await fetch_candidate(candidate_id)
    jobs = await fetch_jobs()

    return match_candidate_to_jobs(candidate, jobs)


@app.get("/match/job/{job_id}", response_model=List[MatchResult])
async def match_for_job(job_id: str) -> List[MatchResult]:
    """
    Match a specific job against all available candidates.

    Args:
        job_id (str): The unique ID of the job to match.

    Returns:
        List[MatchResult]: A sorted list of candidates ranked by match score.

    Raises:
        HTTPException: If the job is not found or if candidate fetch fails.
    """
    job = await fetch_job(job_id)

    # Fetch all candidates
    candidates = await fetch_candidates()

    # Evaluate match score for each candidate
    results: List[MatchResult] = [
        MatchResult(jobId=job.id, jobTitle=cand.name, matchScore=ai_score(cand, job))
        for cand in candidates
    ]

    return sorted(results, key=lambda x: x.matchScore, reverse=True)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    print("✅ AI Matcher Service Started")
    consume_candidates()
