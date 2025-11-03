from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="hr")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)
    content_type = Column(String(100), nullable=True)
    text_content = Column(Text, nullable=True)
    candidate_name = Column(String(255), nullable=True)
    candidate_email = Column(String(255), nullable=True)
    skills = Column(Text, nullable=True)
    total_experience_years = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    s3_url = Column(String, nullable=True)
    matches = relationship("Match", back_populates="resume", cascade="all, delete-orphan")



class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description_text = Column(Text, nullable=False)
    skills = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 
    file_url = Column(String(512), nullable=True)
    matches = relationship("Match", back_populates="job_description", cascade="all, delete-orphan")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    matched_skills = Column(Text)    
    missing_skills = Column(Text)       
    explanations = Column(Text)         
    resume_s3_url = Column(String, nullable=True)
    jd_s3_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resume = relationship("Resume", back_populates="matches")
    job_description = relationship("JobDescription", back_populates="matches")