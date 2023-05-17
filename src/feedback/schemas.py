from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Integer, Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.mysql import SMALLINT

from auth.models import user
from database import Base
from question.models import question


class FeedbackRead(BaseModel):
    rating: int
    feedback_title: str
    question_id: int


class FeedbackCreate(BaseModel):
    rating: int
    feedback_title: str
    user_id: int
    question_id: int
    question_author_id: int


class FeedbackUpdate(BaseModel):
    rating: int
    feedback_title: str


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    rating = Column(SMALLINT(unsigned=True), nullable=False)
    feedback_title = Column(String(length=255, collation="utf8mb4_unicode_ci"), nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey(user.c.id), nullable=False)
    question_id = Column(Integer, ForeignKey(question.c.id), nullable=False)
    question_author_id = Column(Integer, ForeignKey(user.c.id), nullable=False)
