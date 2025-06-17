from pydantic import BaseModel
from typing import List


class Candidate(BaseModel):
    """
    Represents a job candidate profile.

    Attributes:
        id (str): Unique identifier for the candidate.
        name (str): Full name of the candidate.
        skills (List[str]): List of technical and soft skills.
        experienceYears (int): Number of years of professional experience.
        resumeText (str): Full text content of the candidate's resume.
    """
    id: str
    name: str
    skills: List[str]
    experienceYears: int
    resumeText: str


class Job(BaseModel):
    """
    Represents a job posting or opening.

    Attributes:
        id (str): Unique identifier for the job.
        title (str): Title or name of the job position.
        description (str): Full job description including responsibilities.
        requiredSkills (List[str]): List of skills required for the job.
        minExperience (int): Minimum years of experience required.
    """
    id: str
    title: str
    description: str
    requiredSkills: List[str]
    minExperience: int


class MatchResult(BaseModel):
    """
    Represents the AI-generated match score between a candidate and a job.

    Attributes:
        jobId (str): ID of the matched job.
        jobTitle (str): Title of the matched job.
        matchScore (float): Score representing how well the candidate matches the job (range 0–1).
    """
    jobId: str
    jobTitle: str
    matchScore: float
