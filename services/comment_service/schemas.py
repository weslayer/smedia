from pydantic import BaseModel, Field, validator, constr, computed_field
from pydantic.types import StringConstraints
from typing import Optional, List, Annotated
from datetime import datetime
import re

class CommentBase(BaseModel):
    content: Annotated[str, StringConstraints(min_length=1, max_length=1000)] = Field(..., description="Comment text")

    @validator('content')
    def validate_content(cls, v):
        # Clean the content but preserve @ mentions
        v = v.strip()
        if not v:
            raise ValueError("Content cannot be empty")
        return v

class TopLevelCommentCreate(CommentBase):
    post_id: int
    rating: int = Field(..., description="Rating from 1 to 5", ge=1, le=5)

class ReplyCommentCreate(CommentBase):
    post_id: int
    parent_id: int

class CommentCreate(BaseModel):
    content: Annotated[str, StringConstraints(min_length=1, max_length=1000)]
    post_id: int
    parent_id: Optional[int] = None
    rating: Optional[int] = None

    @validator('rating')
    def validate_rating(cls, v, values):
        if 'parent_id' in values:
            if values['parent_id'] is not None and v is not None:
                raise ValueError("Reply comments cannot have ratings")
            return v
        if v is None:
            raise ValueError("Top-level comments must have a rating")
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

class CommentUpdate(BaseModel):
    content: Optional[Annotated[str, StringConstraints(min_length=1, max_length=1000)]] = None
    rating: Optional[int] = Field(None, ge=1, le=5)

    @validator('rating')
    def validate_rating_update(cls, v, values):
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v

class CommentResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    content: str
    rating: Optional[int] = None
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_reply: bool = Field(default=False, description="Indicates if this is a reply to another comment")

    @computed_field
    def is_reply(self) -> bool:
        return self.parent_id is not None

    class Config:
        from_attributes = True 