from pydantic import BaseModel
from typing import List

class Candidate(BaseModel):
    id: str
    name: str
    skills: List[str]
    experienceYears: int
    resumeText: str

class Job(BaseModel):
    id: str
    title: str
    description: str
    requiredSkills: List[str]
    minExperience: int

class MatchResult(BaseModel):
    jobId: str
    jobTitle: str
    matchScore: float
