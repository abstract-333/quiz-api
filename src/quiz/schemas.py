from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from database import Base
from section.models import section


class QuizRead(BaseModel):
    resolve_time: int
    question: str
    choices: list
    answer: str
    type: str


class QuizCreate(BaseModel):
    resolve_time: int
    question: str
    choices: list
    answer: str
    added_by: str
    type: str


class Quiz(Base):
    __tablename__ = "Quiz"
    id = Column(Integer, primary_key=True)
    resolve_time = Column(Integer, nullable=False)
    question = Column(String(length=200), nullable=False)
    choices = Column(JSON, nullable=False)
    answer = Column(String(length=25), nullable=False)
    added_by = Column(String(length=25), nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    section_id = Column(Integer, ForeignKey(section.c.id), nullable=False)
