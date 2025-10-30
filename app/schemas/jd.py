from typing import List, Optional
from pydantic import BaseModel, Field


class JobDescriptionCreate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description_text: str


class JobDescriptionResponse(BaseModel):
    job_description_id: int
    title: Optional[str]
    skills: List[str] = Field(default_factory=list) 