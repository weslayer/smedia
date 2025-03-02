from pydantic import BaseModel, Field, validator, constr
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile
import bleach

class PostBase(BaseModel):
    content: constr(min_length=1, max_length=5000)
    job_title: constr(min_length=1, max_length=100)
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    is_open_to_work: Optional[bool] = True

    @validator('content')
    def sanitize_content(cls, v):
        # Configure allowed HTML tags and attributes
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li']
        allowed_attrs = {}
        
        # Sanitize the content
        clean_content = bleach.clean(
            v,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
        return clean_content

    @validator('job_title')
    def sanitize_job_title(cls, v):
        # Remove any HTML tags from job title
        clean_title = bleach.clean(v, tags=[], strip=True)
        return clean_title

    @validator('skills')
    def sanitize_and_validate_skills(cls, v):
        if v is not None:
            # Remove any HTML tags
            clean_skills = bleach.clean(v, tags=[], strip=True)
            # Split skills and validate
            skills_list = [skill.strip() for skill in clean_skills.split(',')]
            # Remove empty skills and join back
            valid_skills = ','.join([skill for skill in skills_list if skill])
            if not valid_skills:
                raise ValueError('At least one valid skill must be provided')
            return valid_skills
        return v

    @validator('experience_years')
    def validate_experience(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('Experience years cannot be negative')
            if v > 100:
                raise ValueError('Experience years seems unrealistic')
        return v

class PostCreate(PostBase):
    user_id: int
    resume_file: UploadFile

class PostUpdate(PostBase):
    content: Optional[constr(min_length=1, max_length=5000)] = None
    job_title: Optional[constr(min_length=1, max_length=100)] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    is_open_to_work: Optional[bool] = None

    @validator('content')
    def sanitize_content(cls, v):
        if v is not None:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li']
            allowed_attrs = {}
            return bleach.clean(v, tags=allowed_tags, attributes=allowed_attrs, strip=True)
        return v

    @validator('job_title')
    def sanitize_job_title(cls, v):
        if v is not None:
            return bleach.clean(v, tags=[], strip=True)
        return v

    @validator('skills')
    def sanitize_and_validate_skills(cls, v):
        if v is not None:
            clean_skills = bleach.clean(v, tags=[], strip=True)
            skills_list = [skill.strip() for skill in clean_skills.split(',')]
            valid_skills = ','.join([skill for skill in skills_list if skill])
            if not valid_skills:
                raise ValueError('At least one valid skill must be provided')
            return valid_skills
        return v

    @validator('experience_years')
    def validate_experience(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('Experience years cannot be negative')
            if v > 100:
                raise ValueError('Experience years seems unrealistic')
        return v

class PostResponse(PostBase):
    id: int
    user_id: int
    resume_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 