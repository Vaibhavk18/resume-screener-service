from typing import List, Optional
from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    resume_id: int
    filename: str
    parser: str
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    skills: List[str] = Field(default_factory=list)
    total_experience_years: Optional[int]
    s3_url: Optional[str]


class ResultsResponse(BaseModel):
    resume_id: int
    job_description_id: int
    score: int
    matched_skills: List[str]
    missing_skills: List[str]
    explanations: List[str] 

class ResultsResponse(BaseModel):
    resume_id: int
    job_description_id: int
    score: int
    matched_skills: List[str]
    missing_skills: List[str]
    explanations: List[str]
    s3_url: Optional[str]


class BulkResultItem(BaseModel):
    resume_id: int
    job_description_id: int
    score: int
    matched_skills: List[str]
    missing_skills: List[str]
    explanations: List[str]
    resume_s3_url: Optional[str]
    jd_s3_url: Optional[str]


class BulkResultsResponse(BaseModel):
    job_description_id: int
    job_description_title: Optional[str]
    total_resumes_processed: int
    average_score: float
    results: List[BulkResultItem]
