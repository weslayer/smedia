from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile

class PostBase(BaseModel):
    content: str = Field(..., description="Description or summary of your resume")
    job_title: str = Field(..., description="Your current or desired job title")

class PostCreate(PostBase):
    user_id: int
    resume_file: UploadFile

class PostUpdate(PostBase):
    content: Optional[str] = None
    job_title: Optional[str] = None
    skills: Optional[str] = None

class PostResponse(PostBase):
    id: int
    user_id: int
    resume_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 