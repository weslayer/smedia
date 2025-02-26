from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    content: str = Field(..., description="Comment text")
    rating: int = Field(..., description="Rating from 1 to 5", ge=1, le=5)

class CommentCreate(CommentBase):
    post_id: int

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)

class CommentResponse(CommentBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 