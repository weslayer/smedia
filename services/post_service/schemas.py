from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import UploadFile

class PostBase(BaseModel):
    content: str
    media_url: Optional[str] = None

class PostCreate(PostBase):
    user_id: int
    media_file: Optional[UploadFile] = None

class PostUpdate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 