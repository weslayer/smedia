from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas, database, auth
from database import engine
from auth import get_current_user
from middleware import error_handler
from s3 import s3_handler
from sqlalchemy import or_

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Post Service")
app.middleware("http")(error_handler)

@app.post("/posts/", response_model=schemas.PostResponse)
async def create_post(
    content: str,
    job_title: str,
    resume_file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(get_current_user)
):
    # Upload resume
    resume_url = await s3_handler.upload_file(resume_file, file_type="resume")
    
    # Create post
    db_post = models.Post(
        content=content,
        job_title=job_title,
        resume_url=resume_url,
        user_id=current_user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/{post_id}", response_model=schemas.PostResponse)
async def get_post(post_id: int, db: Session = Depends(database.get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/posts/user/{user_id}", response_model=List[schemas.PostResponse])
async def get_user_posts(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    posts = db.query(models.Post)\
        .filter(models.Post.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return posts

@app.put("/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    db: Session = Depends(database.get_db)
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    for key, value in post_update.dict().items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(get_current_user)
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if the user owns the post
    if db_post.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete posts of other users"
        )
    
    # Delete associated media file if exists
    if db_post.resume_url:
        s3_handler.delete_file(db_post.resume_url)
    
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/posts/search/", response_model=List[schemas.PostResponse])
async def search_posts(
    job_title: Optional[str] = None,
    skills: Optional[str] = None,
    min_experience: Optional[int] = None,
    open_to_work: Optional[bool] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Post)
    
    if job_title:
        query = query.filter(models.Post.job_title.ilike(f"%{job_title}%"))
    if skills:
        # Search for any of the provided skills
        skill_list = [skill.strip() for skill in skills.split(',')]
        skill_filters = [models.Post.skills.ilike(f"%{skill}%") for skill in skill_list]
        query = query.filter(or_(*skill_filters))
    if min_experience is not None:
        query = query.filter(models.Post.experience_years >= min_experience)
    if open_to_work is not None:
        query = query.filter(models.Post.is_open_to_work == open_to_work)
    
    return query.order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all() 