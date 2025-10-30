from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import JobDescription
from app.routes.auth import hr_required
from app.utils.nlp import extract_skills
from app.schemas.jd import JobDescriptionCreate, JobDescriptionResponse

router = APIRouter()


@router.post("/job_description", response_model=JobDescriptionResponse)
async def create_job_description(
    payload: JobDescriptionCreate,
    _: dict = Depends(hr_required),
    db: Session = Depends(get_db),
):
    if not payload.description_text or not payload.description_text.strip():
        raise HTTPException(status_code=400, detail="description_text is required")

    skills = extract_skills(payload.description_text)
    jd = JobDescription(
        title=payload.title,
        description_text=payload.description_text,
        skills=", ".join(skills) if skills else None,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)

    return JobDescriptionResponse(
        job_description_id=jd.id,
        title=jd.title,
        skills=skills,
    ) 