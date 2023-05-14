from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON
from database import Base
from section.models import section


class QuestionRead(BaseModel):
    resolve_time: int
    question_title: str
    choices: set
    answer: str


class QuestionCreate(BaseModel):
    resolve_time: int
    question_title: str
    choices: list
    answer: str
    added_by: str



class SoftwareQuestion(Base):
    __tablename__ = "software_questions"
    id = Column(Integer, primary_key=True)
    resolve_time = Column(Integer, nullable=False)
    question_title = Column(String(length=200), nullable=False)
    choices = Column(JSON, nullable=False)
    answer = Column(String(length=25), nullable=False)
    added_by = Column(String(length=25), nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    section_id = Column(Integer, ForeignKey(section.c.id), default=1)


class NetworkQuestion(Base):
    __tablename__ = "network_questions"
    id = Column(Integer, primary_key=True)
    resolve_time = Column(Integer, nullable=False)
    question_title = Column(String(length=200), nullable=False)
    choices = Column(JSON, nullable=False)
    answer = Column(String(length=25), nullable=False)
    added_by = Column(String(length=25), nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    section_id = Column(Integer, ForeignKey(section.c.id), default=2)


class AIQuestion(Base):
    __tablename__ = "ai_questions"
    id = Column(Integer, primary_key=True)
    resolve_time = Column(Integer, nullable=False)
    question_title = Column(String(length=200), nullable=False)
    choices = Column(JSON, nullable=False)
    answer = Column(String(length=25), nullable=False)
    added_by = Column(String(length=25), nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    section_id = Column(Integer, ForeignKey(section.c.id), default=3)
