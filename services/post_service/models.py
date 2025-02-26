from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from shared.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    content = Column(Text)  # Description or summary of the resume
    resume_url = Column(String)  # URL to the PDF resume (now required)
    job_title = Column(String, index=True)  # Job title/role
    skills = Column(String)  # Comma-separated list of skills
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 