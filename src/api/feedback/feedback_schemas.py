from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Integer, Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.mysql import SMALLINT

from api.auth.auth_models import user
from api.question.question_models import question
from db.database import Base


class FeedbackRead(BaseModel):
    rating: int
    feedback_title: Optional[str] = None
    question_id: int


class FeedbackCreate(BaseModel):
    rating: int
    feedback_title: Optional[str] = None
    user_id: int
    question_id: int
    question_author_id: int


class FeedbackUpdate(BaseModel):
    rating: int
    feedback_title: Optional[str] = None


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    rating = Column(SMALLINT(unsigned=True), nullable=False)
    feedback_title = Column(String(length=255), nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey(user.c.id), nullable=False)
    question_id = Column(Integer, ForeignKey(question.c.id), nullable=False)
    question_author_id = Column(Integer, ForeignKey(user.c.id), nullable=False)
