from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import JobDescription, Resume
from app.routes.auth import hr_required
from app.utils.scoring import score_resume_against_jd
from app.schemas.resume import ResultsResponse

router = APIRouter()


@router.get("/results/{resume_id}", response_model=ResultsResponse)
async def get_results(resume_id: int, _: dict = Depends(hr_required), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    jd = db.query(JobDescription).order_by(JobDescription.created_at.desc()).first()
    if not jd:
        raise HTTPException(status_code=404, detail="No job description found")

    result = score_resume_against_jd(resume.text_content, jd.description_text)
    return ResultsResponse(
        resume_id=resume.id,
        job_description_id=jd.id,
        score=result["score"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        explanations=result["explanations"],
        s3_url=resume.s3_url
    ) 