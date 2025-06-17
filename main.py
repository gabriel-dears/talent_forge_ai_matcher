import os
import httpx
from fastapi import FastAPI, HTTPException
from typing import List
from models import Candidate, Job, MatchResult
from matcher import match_candidate_to_jobs, ai_score

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
    async with httpx.AsyncClient() as client:
        # Fetch candidate data from external Spring Boot API
        cand_resp = await client.get(f"{SPRING_BASE}/candidates/{candidate_id}")
        if cand_resp.status_code != 200:
            raise HTTPException(status_code=cand_resp.status_code, detail="Candidate not found")
        candidate = Candidate(**cand_resp.json())

        # Fetch all jobs (pagination support via ?size=1000)
        jobs_resp = await client.get(f"{SPRING_BASE}/jobs?size=1000")
        if jobs_resp.status_code != 200:
            raise HTTPException(status_code=jobs_resp.status_code, detail="Jobs fetch failed")
        jobs_data = jobs_resp.json().get("content", [])
        jobs = [Job(**j) for j in jobs_data]

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
    async with httpx.AsyncClient() as client:
        # Fetch job details
        job_resp = await client.get(f"{SPRING_BASE}/jobs/{job_id}")
        if job_resp.status_code != 200:
            raise HTTPException(status_code=job_resp.status_code, detail="Job not found")
        job = Job(**job_resp.json())

        # Fetch all candidates
        cands_resp = await client.get(f"{SPRING_BASE}/candidates?size=1000")
        if cands_resp.status_code != 200:
            raise HTTPException(status_code=cands_resp.status_code, detail="Candidates fetch failed")
        cands_data = cands_resp.json().get("content", [])
        candidates = [Candidate(**c) for c in cands_data]

    # Evaluate match score for each candidate
    results: List[MatchResult] = [
        MatchResult(jobId=job.id, jobTitle=cand.name, matchScore=ai_score(cand, job))
        for cand in candidates
    ]

    return sorted(results, key=lambda x: x.matchScore, reverse=True)
