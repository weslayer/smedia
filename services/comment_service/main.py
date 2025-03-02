from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import models, schemas
from shared.database import engine, get_db
from shared.auth import get_current_user
from shared.middleware import error_handler
import re

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Comment Service")
app.middleware("http")(error_handler)

def extract_mentions(content: str) -> List[str]:
    """Extract @ mentions from comment content"""
    return [username.strip() for username in re.findall(r'@(\w+)', content)]

@app.post("/comments/", response_model=schemas.CommentResponse)
async def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    # Validate parent comment if it exists
    if comment.parent_id:
        parent_comment = db.query(models.Comment).filter(models.Comment.id == comment.parent_id).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent_comment.parent_id:
            raise HTTPException(status_code=400, detail="Cannot nest comments more than one level deep")
        if comment.rating is not None:
            raise HTTPException(status_code=400, detail="Reply comments cannot have ratings")
    else:
        # Top-level comment must have a rating
        if comment.rating is None:
            raise HTTPException(status_code=400, detail="Top-level comments must have a rating")
        if not 1 <= comment.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    # Create comment
    db_comment = models.Comment(
        content=comment.content,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        rating=comment.rating if not comment.parent_id else None,
        user_id=current_user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/post/{post_id}", response_model=List[schemas.CommentResponse])
async def get_post_comments(
    post_id: int,
    parent_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(models.Comment).filter(models.Comment.post_id == post_id)
    
    # Filter by parent_id (None for top-level comments, specific ID for replies)
    query = query.filter(models.Comment.parent_id == parent_id)
    
    # Order by creation date, with top-level comments ordered by rating as well
    if parent_id is None:
        query = query.order_by(models.Comment.rating.desc(), models.Comment.created_at.desc())
    else:
        query = query.order_by(models.Comment.created_at.asc())
    
    return query.offset(skip).limit(limit).all()

@app.get("/comments/{comment_id}/replies", response_model=List[schemas.CommentResponse])
async def get_comment_replies(
    comment_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    # Verify comment exists
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Get replies
    replies = db.query(models.Comment)\
        .filter(models.Comment.parent_id == comment_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return replies

@app.get("/comments/average-rating/{post_id}")
async def get_post_average_rating(post_id: int, db: Session = Depends(get_db)):
    result = db.query(func.avg(models.Comment.rating))\
        .filter(models.Comment.post_id == post_id)\
        .scalar()
    
    return {
        "post_id": post_id,
        "average_rating": float(result) if result else None,
        "total_ratings": db.query(models.Comment)\
            .filter(models.Comment.post_id == post_id)\
            .count()
    }

@app.put("/comments/{comment_id}", response_model=schemas.CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    # Get existing comment
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Verify ownership
    if db_comment.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    
    # Prevent setting rating on replies
    if db_comment.parent_id is not None and comment_update.rating is not None:
        raise HTTPException(status_code=400, detail="Cannot set rating on reply comments")
    
    # Update fields
    for field, value in comment_update.dict(exclude_unset=True).items():
        setattr(db_comment, field, value)
    
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if db_comment.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot delete other users' comments")
    
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 