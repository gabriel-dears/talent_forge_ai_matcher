import httpx
from fastapi import FastAPI, HTTPException

from consts import SPRING_BASE
from models import Candidate


async def fetch_candidate(candidate_id: str) -> Candidate:
    async with httpx.AsyncClient() as client:
        # Fetch candidate data from external Spring Boot API
        cand_resp = await client.get(f"{SPRING_BASE}/candidates/{candidate_id}")
        if cand_resp.status_code != 200:
            raise HTTPException(status_code=cand_resp.status_code, detail="Candidate not found")
        return Candidate(**cand_resp.json())

async def fetch_candidates() -> list[Candidate]:
    async with httpx.AsyncClient() as client:
        # Fetch candidate data from external Spring Boot API
        candidates_response = await client.get(f"{SPRING_BASE}/candidates?size=1000")
        if candidates_response.status_code != 200:
            raise HTTPException(status_code=candidates_response.status_code, detail="Candidates fetch failed")
        candidates_data = candidates_response.json().get("content", [])
        return [Candidate(**c) for c in candidates_data]
