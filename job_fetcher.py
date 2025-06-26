import httpx
from fastapi import FastAPI, HTTPException

from consts import SPRING_BASE
from models import Job


async def fetch_jobs() -> list[Job]:
    async with httpx.AsyncClient() as client:
        # Fetch all jobs (pagination support via ?size=1000)
        jobs_resp = await client.get(f"{SPRING_BASE}/jobs?size=1000")
        if jobs_resp.status_code != 200:
            raise HTTPException(status_code=jobs_resp.status_code, detail="Jobs fetch failed")
        jobs_data = jobs_resp.json().get("content", [])
        return[Job(**j) for j in jobs_data]

async def fetch_job(job_id: str) -> Job:
    async with httpx.AsyncClient() as client:
        # Fetch job details
        job_resp = await client.get(f"{SPRING_BASE}/jobs/{job_id}")
        if job_resp.status_code != 200:
            raise HTTPException(status_code=job_resp.status_code, detail="Job not found")
        return Job(**job_resp.json())
