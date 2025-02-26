from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import models, schemas
from shared.database import engine, get_db
from shared.auth import get_current_user
from shared.middleware import error_handler

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Comment Service")
app.middleware("http")(error_handler)

@app.post("/comments/", response_model=schemas.CommentResponse)
async def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    db_comment = models.Comment(
        **comment.model_dump_json(),
        user_id=current_user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/post/{post_id}", response_model=List[schemas.CommentResponse])
async def get_post_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    comments = db.query(models.Comment)\
        .filter(models.Comment.post_id == post_id)\
        .order_by(models.Comment.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return comments

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
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if db_comment.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot update other users' comments")
    
    for key, value in comment_update.dict(exclude_unset=True).items():
        setattr(db_comment, key, value)
    
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