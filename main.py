from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from matcher import match_candidate_to_jobs
from models import Candidate, Job, MatchResult

app = FastAPI()

class MatchRequest(BaseModel):
    candidate: Candidate
    jobs: List[Job]

@app.post("/match", response_model=List[MatchResult])
def match(match_request: MatchRequest):
    try:
        results = match_candidate_to_jobs(match_request.candidate, match_request.jobs)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
