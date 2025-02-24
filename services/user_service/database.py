from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from tenacity import retry, stop_after_attempt, wait_exponential

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://devuser:devpassword@postgres:5432/socialapp")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_db():
    db = SessionLocal()
    try:
        # Test the connection
        db.execute("SELECT 1")
        yield db
    finally:
        db.close() 