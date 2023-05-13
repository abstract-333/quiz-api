from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON
from database import Base
from section.models import section


class QuestionRead(BaseModel):
    resolve_time: int
    question_title: str
    choices: list
    answer: str


class QuestionCreate(BaseModel):
    resolve_time: int
    question_title: str
    choices: list
    answer: str
    added_by: str


class Question(Base):
    __tablename__ = "Question"
    id = Column(Integer, primary_key=True)
    resolve_time = Column(Integer, nullable=False)
    question_title = Column(String(length=200), nullable=False)
    choices = Column(JSON, nullable=False)
    answer = Column(String(length=25), nullable=False)
    added_by = Column(String(length=25), nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    section_id = Column(Integer, ForeignKey(section.c.id))
