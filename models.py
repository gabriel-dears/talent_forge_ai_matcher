from datetime import date
from typing import List, Any

from pydantic import BaseModel, field_validator, model_validator


class Resume(BaseModel):
    text: str
    filePath: str

class Candidate(BaseModel):
    id: str
    name: str
    email: str
    resume: Resume
    skills: List[str]
    experienceYears: int
    dateNotification: date

    @model_validator(mode="before")
    @classmethod
    def normalize_date_notification(cls, data: Any) -> Any:
        """
        Transforms dateNotification from list format [YYYY, MM, DD] to `date`
        object if needed.
        """
        if isinstance(data, dict):
            raw_date = data.get("dateNotification")
            if isinstance(raw_date, list) and len(raw_date) == 3:
                try:
                    data["dateNotification"] = date(*raw_date)
                except Exception as e:
                    raise ValueError(f"Invalid dateNotification format: {raw_date}") from e
        return data


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
