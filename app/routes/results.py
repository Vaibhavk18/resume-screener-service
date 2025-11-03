from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import JobDescription, Resume, Match
from app.routes.auth import hr_required
from app.utils.scoring import score_resume_against_jd
from app.schemas.resume import ResultsResponse, BulkResultsResponse, BulkResultItem

router = APIRouter()


@router.post("/results", response_model=ResultsResponse)
async def match_resume_to_jd(
    resume_id: int = Query(..., description="ID of the resume to evaluate"),
    job_description_id: int = Query(..., description="ID of the job description to compare against"),
    _: dict = Depends(hr_required),
    db: Session = Depends(get_db),
):
    

    # --- Validate resume existence ---
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # --- Validate JD existence ---
    jd = db.query(JobDescription).filter(JobDescription.id == job_description_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    # --- Perform scoring ---
    result = score_resume_against_jd(resume.text_content, jd.description_text)

    return ResultsResponse(
        resume_id=resume.id,
        job_description_id=jd.id,
        score=result["score"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        explanations=result["explanations"],
        s3_url=resume.s3_url,
    )

@router.get("/results/bulk", response_model=BulkResultsResponse)
async def get_bulk_results(
    job_description_id: int,
    _: dict = Depends(hr_required),
    db: Session = Depends(get_db),
):
    """Compare all resumes in DB against a specific JD and return summarized results."""
    jd = db.query(JobDescription).filter(JobDescription.id == job_description_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    resumes = db.query(Resume).all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found")

    results = []
    total_score = 0

    for resume in resumes:
        result = score_resume_against_jd(resume.text_content, jd.description_text)

        match_entry = Match(
            resume_id=resume.id,
            job_description_id=jd.id,
            score=result["score"],
            matched_skills=", ".join(result["matched_skills"]),
            missing_skills=", ".join(result["missing_skills"]),
            explanations="\n".join(result["explanations"]),
            resume_s3_url=resume.s3_url,
            jd_s3_url=jd.s3_url if hasattr(jd, "s3_url") else None,
        )
        db.add(match_entry)

        results.append(
            BulkResultItem(
                resume_id=resume.id,
                job_description_id=jd.id,
                score=result["score"],
                matched_skills=result["matched_skills"],
                missing_skills=result["missing_skills"],
                explanations=result["explanations"],
                resume_s3_url=resume.s3_url,
                jd_s3_url=jd.s3_url if hasattr(jd, "s3_url") else None,
            )
        )
        total_score += result["score"]

    db.commit()

    avg_score = total_score / len(results) if results else 0

    return BulkResultsResponse(
        job_description_id=jd.id,
        job_description_title=jd.title,
        total_resumes_processed=len(results),
        average_score=round(avg_score, 2),
        results=results,
    )
