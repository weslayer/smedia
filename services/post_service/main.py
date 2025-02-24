from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .database import engine
from .auth import get_current_user
from .middleware import error_handler

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Post Service")
app.middleware("http")(error_handler)

@app.post("/posts/", response_model=schemas.PostResponse)
async def create_post(
    post: schemas.PostCreate, 
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(get_current_user)
):
    # Verify the post is created by the authenticated user
    if post.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot create posts for other users"
        )
    
    db_post = models.Post(**post.dict())
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
    
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"} 