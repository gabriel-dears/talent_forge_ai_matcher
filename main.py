import os
import httpx
from fastapi import FastAPI, HTTPException
from typing import List
from models import Candidate, Job, MatchResult
from matcher import match_candidate_to_jobs, ai_score

app = FastAPI()

# base URL of your Spring Boot API, e.g. "http://spring-app:8080/api/v1"
SPRING_BASE = os.getenv("SPRING_API_URL", "http://localhost:8080/api/v1")


@app.get("/match/candidate/{candidate_id}", response_model=List[MatchResult])
async def match_for_candidate(candidate_id: str):
    async with httpx.AsyncClient() as client:
        # fetch candidate
        cand_resp = await client.get(f"{SPRING_BASE}/candidates/{candidate_id}")
        if cand_resp.status_code != 200:
            raise HTTPException(status_code=cand_resp.status_code, detail="Candidate not found")
        candidate = Candidate(**cand_resp.json())

        # fetch jobs
        jobs_resp = await client.get(f"{SPRING_BASE}/jobs?size=1000")
        jobs_data = jobs_resp.json().get("content", [])
        jobs = [Job(**j) for j in jobs_data]

    # compute matches
    return match_candidate_to_jobs(candidate, jobs)


@app.get("/match/job/{job_id}", response_model=List[MatchResult])
async def match_for_job(job_id: str):
    async with httpx.AsyncClient() as client:
        # fetch job
        job_resp = await client.get(f"{SPRING_BASE}/jobs/{job_id}")
        if job_resp.status_code != 200:
            raise HTTPException(status_code=job_resp.status_code, detail="Job not found")
        job = Job(**job_resp.json())

        # fetch candidates
        cands_resp = await client.get(f"{SPRING_BASE}/candidates?size=1000")
        cands_data = cands_resp.json().get("content", [])
        candidates = [Candidate(**c) for c in cands_data]

    # reuse matcher by swapping args
    # build a dummy candidate list-to-job match result list
    # but here we need to return CandidateResponse-like; for simplicity we wrap into MatchResult
    results = []
    for cand in candidates:
        score = ai_score(cand, job)
        results.append(MatchResult(jobId=job.id, jobTitle=cand.name, matchScore=score))
    return sorted(results, key=lambda x: x.matchScore, reverse=True)
