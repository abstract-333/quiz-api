from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from typing import Optional
from auth.auth_models import user
from database import Base
from section.section_models import section


class QuestionRead(BaseModel):
    question_title: str
    choices: set
    answer: str
    reference: str
    reference_link: Optional[str] = None
    active: Optional[bool]


class QuestionCreate(BaseModel):
    question_title: str
    choices: list
    answer: str
    added_by: int
    section_id: int
    reference: str
    reference_link: Optional[str]
    active: bool = False


class QuestionUpdate(BaseModel):
    question_title: str
    choices: list
    answer: str
    reference: str
    reference_link: Optional[str] = None
    active: bool


class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True)
    question_title = Column(String(length=200), nullable=False)
    choices = Column(JSON, nullable=False)
    answer = Column(String(length=25), nullable=False)
    reference = Column(String(length=100), nullable=False)
    reference_link = Column(String(length=200), nullable=True)
    added_by = Column(Integer, ForeignKey(user.c.id), nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    section_id = Column(Integer, ForeignKey(section.c.id))
    active = Column(Boolean, default=False, nullable=False)
