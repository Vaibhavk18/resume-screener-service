from typing import Dict
from io import BytesIO
import traceback
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import Resume
from app.routes.auth import hr_required
from app.utils.parsers import extract_text
from app.utils.nlp import extract_fields
from app.schemas.resume import ResumeUploadResponse
from app.utils.s3_client import upload_resume as upload_to_s3  

router = APIRouter()

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


@router.post("/upload_resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    _: Dict = Depends(hr_required),
    db: Session = Depends(get_db),
):
    """
    Upload and parse a candidate resume.
    - Extracts text and metadata (name, email, skills, exp)
    - Uploads to S3/resumes/
    - Stores all metadata and URL in database
    """

    # --- Validate content type ---
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported content type")

    # --- Read file ---
    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to read uploaded file")

    if not contents or len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    # --- Extract text ---
    try:
        text, used_parser = extract_text(file.filename, file.content_type or "", contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    # --- Extract candidate info ---
    fields = extract_fields(text)

    # --- Upload to S3 ---
    try:
        file_obj = BytesIO(contents)
        s3_url = await upload_to_s3(
            file_obj,
            file.filename,
            content_type=file.content_type,
            folder="resumes"
        )
    except Exception as e:
        print("S3 upload failed:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")

    # --- Save to DB ---
    try:
        resume = Resume(
            filename=file.filename,
            content_type=file.content_type or used_parser,
            text_content=text,
            candidate_name=fields.get("candidate_name"),
            candidate_email=fields.get("candidate_email"),
            skills=fields.get("skills"),
            total_experience_years=fields.get("total_experience_years"),
            s3_url=s3_url,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
    except Exception as e:
        db.rollback()
        print("❌ Database Error:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save resume")

    return ResumeUploadResponse(
        resume_id=resume.id,
        filename=resume.filename,
        parser=used_parser,
        candidate_name=resume.candidate_name,
        candidate_email=resume.candidate_email,
        skills=resume.skills.split(", ") if resume.skills else [],
        total_experience_years=resume.total_experience_years,
        s3_url=resume.s3_url,
    )
