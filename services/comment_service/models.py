from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.sql import func
from shared.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    post_id = Column(Integer, index=True)
    content = Column(Text)
    rating = Column(Integer, nullable=True)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Ensure rating is between 1 and 5 when present, parent_id is not self-referential,
    # and replies don't have ratings
    __table_args__ = (
        CheckConstraint('(rating IS NULL AND parent_id IS NOT NULL) OR (rating BETWEEN 1 AND 5 AND parent_id IS NULL)', 
                       name='valid_rating_and_nesting'),
        CheckConstraint('id != parent_id', name='prevent_self_reference'),
    ) 