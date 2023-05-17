from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON

from auth.models import user
from database import Base
from section.models import section


class QuestionRead(BaseModel):
    question_title: str
    choices: set
    answer: str


class QuestionCreate(BaseModel):
    question_title: str
    choices: list
    answer: str
    added_by: int
    section_id: int


class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True)
    question_title = Column(String(length=200), nullable=False)
    choices = Column(JSON, nullable=False)
    answer = Column(String(length=25), nullable=False)
    added_by = Column(Integer, ForeignKey(user.c.id), nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    section_id = Column(Integer, ForeignKey(section.c.id))

