from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from io import BytesIO

from app.models.database import get_db
from app.models.entities import JobDescription
from app.routes.auth import hr_required
from app.utils.parsers import extract_text
from app.utils.nlp import extract_skills
from app.utils.s3_client import upload_resume as upload_to_s3  
from app.schemas.jd import JobDescriptionResponse

router = APIRouter()


@router.post("/job_description", response_model=JobDescriptionResponse)
async def create_job_description(
    title: Optional[str] = Form(None),
    description_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    _: dict = Depends(hr_required),
    db: Session = Depends(get_db),
):
    """
    Create a Job Description.

    Supports:
    - Plain text or JSON input
    - File uploads (PDF, DOCX, TXT)
    Automatically extracts text, skills, uploads JD file to S3/job_descriptions/.
    """

    extracted_text = None
    s3_url = None

    # --- If JD file uploaded ---
    if jd_file:
        try:
            file_bytes = await jd_file.read()
            extracted_text, used_fmt = extract_text(jd_file.filename, jd_file.content_type, file_bytes)
            if not extracted_text.strip():
                raise HTTPException(status_code=400, detail=f"Failed to extract text from {jd_file.filename}")

            # Upload JD file to S3 
            file_obj = BytesIO(file_bytes)
            s3_url = await upload_to_s3(
                file_obj,
                jd_file.filename,
                content_type=jd_file.content_type,
                folder="job_descriptions"
            )
            description_text = extracted_text

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing JD file: {str(e)}")

    # --- Validate input ---
    if not description_text or not description_text.strip():
        raise HTTPException(status_code=400, detail="Job description text or file is required")

    skills = extract_skills(description_text)

    # --- Save to database ---
    jd = JobDescription(
        title=title or "Untitled JD",
        description_text=description_text,
        skills=", ".join(skills) if skills else None,
        file_url=s3_url
    )

    db.add(jd)
    db.commit()
    db.refresh(jd)

    return JobDescriptionResponse(
        job_description_id=jd.id,
        title=jd.title,
        skills=skills,
        file_url=s3_url,
    )
