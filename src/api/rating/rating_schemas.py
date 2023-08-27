from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP

from api.auth.auth_models import user
from api.university.university_models import university
from db.database import Base


class RatingRead(BaseModel):
    questions_number: int
    solved: int


class RatingCreate(BaseModel):
    user_id: int
    university_id: int
    questions_number: int
    solved: int


class RatingUpdate(BaseModel):
    questions_number: int
    solved: int


class Rating(Base):
    __tablename__ = "rating"
    id = Column(Integer, primary_key=True)
    university_id = Column(Integer, ForeignKey(university.c.id))
    user_id = Column(Integer, ForeignKey(user.c.id))
    questions_number = Column(Integer, nullable=False)
    solved = Column(Integer, nullable=False)
    added_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

