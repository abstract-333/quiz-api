from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP, JSON, Float

from auth.models import user
from database import Base
from section.models import section
from university.models import university


class RatingRead(BaseModel):
    user_id: int
    questions_number: int
    solved: int


class RatingCreate(BaseModel):
    user_id: int
    university_id: int
    questions_number: int
    percent_solved: float


class RatingUpdate(BaseModel):
    user_id: int
    questions_number: int
    percent_solved: float


class Rating(Base):
    __tablename__ = "rating"
    id = Column(Integer, primary_key=True)
    university_id = Column(Integer, ForeignKey(university.c.id))
    user_id = Column(Integer, ForeignKey(user.c.id))
    questions_number = Column(Integer, nullable=False)
    percent_solved = Column(Float, nullable=False)

